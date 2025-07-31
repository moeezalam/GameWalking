package com.example.gamewalking

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.DatagramPacket
import java.net.DatagramSocket
import java.net.InetAddress
import java.net.SocketException

class UDPSender(private val ipAddress: String, private val port: Int) {
    
    private var socket: DatagramSocket? = null
    private var targetAddress: InetAddress? = null
    
    init {
        try {
            socket = DatagramSocket()
            targetAddress = InetAddress.getByName(ipAddress)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    suspend fun sendStep() {
        withContext(Dispatchers.IO) {
            try {
                val message = "STEP"
                val buffer = message.toByteArray()
                
                targetAddress?.let { address ->
                    val packet = DatagramPacket(buffer, buffer.size, address, port)
                    socket?.send(packet)
                }
            } catch (e: SocketException) {
                // Handle socket exceptions (connection issues)
                e.printStackTrace()
            } catch (e: Exception) {
                // Handle other exceptions
                e.printStackTrace()
            }
        }
    }
    
    fun close() {
        try {
            socket?.close()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}