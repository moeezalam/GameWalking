package com.example.gamewalking

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat

class MainActivity : AppCompatActivity() {
    
    private lateinit var ipAddressEditText: EditText
    private lateinit var portEditText: EditText
    private lateinit var startButton: Button
    private lateinit var stopButton: Button
    private lateinit var statusTextView: TextView
    
    private var isServiceRunning = false
    
    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.values.all { it }
        if (allGranted) {
            Toast.makeText(this, "All permissions granted!", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(this, "Permissions required for step detection", Toast.LENGTH_LONG).show()
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initViews()
        checkPermissions()
        setupClickListeners()
    }
    
    private fun initViews() {
        ipAddressEditText = findViewById(R.id.ipAddressEditText)
        portEditText = findViewById(R.id.portEditText)
        startButton = findViewById(R.id.startButton)
        stopButton = findViewById(R.id.stopButton)
        statusTextView = findViewById(R.id.statusTextView)
        
        // Set default values
        ipAddressEditText.setText("youripaddress") // Replace with your PC's IP
        portEditText.setText("9000")
        
        updateUI()
    }
    
    private fun checkPermissions() {
        val permissions = mutableListOf<String>()
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACTIVITY_RECOGNITION) 
                != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.ACTIVITY_RECOGNITION)
            }
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) 
                != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }
        
        if (permissions.isNotEmpty()) {
            requestPermissionLauncher.launch(permissions.toTypedArray())
        }
    }
    
    private fun setupClickListeners() {
        startButton.setOnClickListener {
            startStepDetection()
        }
        
        stopButton.setOnClickListener {
            stopStepDetection()
        }
    }
    
    private fun startStepDetection() {
        val ipAddress = ipAddressEditText.text.toString().trim()
        val port = portEditText.text.toString().trim()
        
        if (ipAddress.isEmpty() || port.isEmpty()) {
            Toast.makeText(this, "Please enter IP address and port", Toast.LENGTH_SHORT).show()
            return
        }
        
        val intent = Intent(this, StepDetectionService::class.java).apply {
            putExtra("ip_address", ipAddress)
            putExtra("port", port.toInt())
        }
        
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(intent)
        } else {
            startService(intent)
        }
        
        isServiceRunning = true
        updateUI()
        Toast.makeText(this, "Step detection started", Toast.LENGTH_SHORT).show()
    }
    
    private fun stopStepDetection() {
        val intent = Intent(this, StepDetectionService::class.java)
        stopService(intent)
        
        isServiceRunning = false
        updateUI()
        Toast.makeText(this, "Step detection stopped", Toast.LENGTH_SHORT).show()
    }
    
    private fun updateUI() {
        if (isServiceRunning) {
            startButton.isEnabled = false
            stopButton.isEnabled = true
            statusTextView.text = "Status: Running"
            ipAddressEditText.isEnabled = false
            portEditText.isEnabled = false
        } else {
            startButton.isEnabled = true
            stopButton.isEnabled = false
            statusTextView.text = "Status: Stopped"
            ipAddressEditText.isEnabled = true
            portEditText.isEnabled = true
        }
    }
}