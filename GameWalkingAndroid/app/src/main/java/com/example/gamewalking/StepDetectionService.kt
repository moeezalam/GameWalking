package com.example.gamewalking

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import androidx.core.app.NotificationCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.launch

class StepDetectionService : Service(), SensorEventListener {
    
    companion object {
        private const val NOTIFICATION_ID = 1
        private const val CHANNEL_ID = "GameWalkingChannel"
    }
    
    private lateinit var sensorManager: SensorManager
    private var stepDetectorSensor: Sensor? = null
    private var stepCounterSensor: Sensor? = null
    private lateinit var udpSender: UDPSender
    private lateinit var wakeLock: PowerManager.WakeLock
    
    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    
    private var initialStepCount = -1
    private var lastStepCount = 0
    
    override fun onCreate() {
        super.onCreate()
        
        sensorManager = getSystemService(Context.SENSOR_SERVICE) as SensorManager
        stepDetectorSensor = sensorManager.getDefaultSensor(Sensor.TYPE_STEP_DETECTOR)
        stepCounterSensor = sensorManager.getDefaultSensor(Sensor.TYPE_STEP_COUNTER)
        
        // Acquire wake lock to keep CPU active
        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(
            PowerManager.PARTIAL_WAKE_LOCK,
            "GameWalking::StepDetectionWakeLock"
        )
        
        createNotificationChannel()
    }
    
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val ipAddress = intent?.getStringExtra("ip_address") ?: "192.168.1.100"
        val port = intent?.getIntExtra("port", 9000) ?: 9000
        
        udpSender = UDPSender(ipAddress, port)
        
        startForeground(NOTIFICATION_ID, createNotification())
        
        // Acquire wake lock
        if (!wakeLock.isHeld) {
            wakeLock.acquire()
        }
        
        // Register sensor listeners
        registerSensorListeners()
        
        return START_STICKY
    }
    
    override fun onDestroy() {
        super.onDestroy()
        
        // Unregister sensor listeners
        sensorManager.unregisterListener(this)
        
        // Release wake lock
        if (wakeLock.isHeld) {
            wakeLock.release()
        }
        
        udpSender.close()
    }
    
    override fun onBind(intent: Intent?): IBinder? = null
    
    private fun registerSensorListeners() {
        // Prefer step detector for real-time detection
        if (stepDetectorSensor != null) {
            sensorManager.registerListener(
                this,
                stepDetectorSensor,
                SensorManager.SENSOR_DELAY_FASTEST
            )
        }
        
        // Also register step counter as backup
        if (stepCounterSensor != null) {
            sensorManager.registerListener(
                this,
                stepCounterSensor,
                SensorManager.SENSOR_DELAY_FASTEST
            )
        }
        
        if (stepDetectorSensor == null && stepCounterSensor == null) {
            // Fallback to accelerometer if step sensors are not available
            val accelerometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER)
            if (accelerometer != null) {
                sensorManager.registerListener(
                    this,
                    accelerometer,
                    SensorManager.SENSOR_DELAY_FASTEST
                )
            }
        }
    }
    
    override fun onSensorChanged(event: SensorEvent?) {
        event?.let { sensorEvent ->
            when (sensorEvent.sensor.type) {
                Sensor.TYPE_STEP_DETECTOR -> {
                    // Step detector triggers for each step
                    onStepDetected()
                }
                
                Sensor.TYPE_STEP_COUNTER -> {
                    // Step counter gives total step count
                    handleStepCounter(sensorEvent.values[0].toInt())
                }
                
                Sensor.TYPE_ACCELEROMETER -> {
                    // Fallback accelerometer-based step detection
                    handleAccelerometerData(sensorEvent.values)
                }
            }
        }
    }
    
    override fun onAccuracyChanged(sensor: Sensor?, accuracy: Int) {
        // Not needed for this implementation
    }
    
    private fun handleStepCounter(currentStepCount: Int) {
        if (initialStepCount == -1) {
            initialStepCount = currentStepCount
            lastStepCount = currentStepCount
            return
        }
        
        if (currentStepCount > lastStepCount) {
            onStepDetected()
            lastStepCount = currentStepCount
        }
    }
    
    // Simple accelerometer-based step detection (fallback)
    private var lastAcceleration = 0f
    private var currentAcceleration = 0f
    private var lastTime = 0L
    private val stepThreshold = 12f
    
    private fun handleAccelerometerData(values: FloatArray) {
        val x = values[0]
        val y = values[1]
        val z = values[2]
        
        lastAcceleration = currentAcceleration
        currentAcceleration = kotlin.math.sqrt((x * x + y * y + z * z).toDouble()).toFloat()
        
        val delta = currentAcceleration - lastAcceleration
        val currentTime = System.currentTimeMillis()
        
        if (kotlin.math.abs(delta) > stepThreshold && currentTime - lastTime > 500) {
            onStepDetected()
            lastTime = currentTime
        }
    }
    
    private fun onStepDetected() {
        serviceScope.launch {
            udpSender.sendStep()
        }
    }
    
    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "GameWalking Service",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Step detection service for GameWalking"
            }
            
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            manager.createNotificationChannel(channel)
        }
    }
    
    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("GameWalking Active")
            .setContentText("Detecting steps for game control")
            .setSmallIcon(android.R.drawable.ic_media_play)
            .setOngoing(true)
            .build()
    }
}