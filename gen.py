import os

def w(path, text):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text.lstrip("\n"))

K = "app/src/main/java/com/salah/app/"
R = "app/src/main/res/"

w("settings.gradle", r'''
pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "PrayerApp"
include ':app'
''')

w("build.gradle", r'''
plugins {
    id 'com.android.application' version '8.2.2' apply false
    id 'org.jetbrains.kotlin.android' version '1.9.22' apply false
}
''')

w("gradle.properties", r'''
org.gradle.jvmargs=-Xmx3g -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
''')

w("app/build.gradle", r'''
plugins {
    id 'com.android.application'
    id 'org.jetbrains.kotlin.android'
}
android {
    namespace 'com.salah.app'
    compileSdk 34
    defaultConfig {
        applicationId 'com.salah.app'
        minSdk 24
        targetSdk 33
        versionCode 1
        versionName '1.0'
    }
    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = '17' }
}
dependencies {
    implementation 'androidx.core:core-ktx:1.12.0'
    implementation 'androidx.activity:activity-ktx:1.8.2'
    implementation 'com.google.mlkit:image-labeling:17.0.7'
}
''')

w("app/src/main/AndroidManifest.xml", r'''
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK"/>
    <uses-permission android:name="android.permission.USE_FULL_SCREEN_INTENT"/>
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
    <uses-permission android:name="android.permission.WAKE_LOCK"/>
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>

    <queries>
        <intent>
            <action android:name="android.intent.action.MAIN"/>
            <category android:name="android.intent.category.LAUNCHER"/>
        </intent>
    </queries>

    <application
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:allowBackup="false"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>

        <activity
            android:name=".BlockActivity"
            android:exported="false"
            android:launchMode="singleTop"
            android:excludeFromRecents="true"/>

        <service
            android:name=".PrayerService"
            android:exported="false"
            android:foregroundServiceType="mediaPlayback"/>

        <service
            android:name=".BlockerService"
            android:exported="true"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService"/>
            </intent-filter>
            <meta-data
                android:name="android.accessibilityservice"
                android:resource="@xml/accessibility_config"/>
        </service>

        <receiver android:name=".AlarmReceiver" android:exported="false"/>

        <receiver android:name=".BootReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED"/>
                <action android:name="android.intent.action.MY_PACKAGE_REPLACED"/>
                <action android:name="android.intent.action.TIME_SET"/>
                <action android:name="android.intent.action.TIMEZONE_CHANGED"/>
            </intent-filter>
        </receiver>

        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths"/>
        </provider>
    </application>
</manifest>
''')

w(R + "values/strings.xml", r'''
<resources>
    <string name="app_name">صلاتي</string>
    <string name="acc_desc">يقفل التطبيقات اللي اخترتها لحد ما تصلي</string>
</resources>
''')

w(R + "xml/accessibility_config.xml", r'''
<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeWindowStateChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault"
    android:canRetrieveWindowContent="false"
    android:notificationTimeout="100"
    android:description="@string/acc_desc"/>
''')

w(R + "xml/file_paths.xml", r'''
<?xml version="1.0" encoding="utf-8"?>
<paths>
    <cache-path name="images" path="images/"/>
</paths>
''')

w(K + "Ui.kt", r'''
package com.salah.app

import android.content.Context
import android.graphics.Color
import android.graphics.Typeface
import android.widget.Button
import android.widget.TextView

object Ui {
    fun dp(c: Context, v: Int): Int = (v * c.resources.displayMetrics.density).toInt()

    fun text(
        c: Context,
        s: String,
        size: Float = 16f,
        bold: Boolean = false,
        color: Int = Color.parseColor("#222222")
    ): TextView {
        val t = TextView(c)
        t.text = s
        t.textSize = size
        t.setTextColor(color)
        if (bold) t.setTypeface(null, Typeface.BOLD)
        return t
    }

    fun button(c: Context, s: String, onClick: () -> Unit): Button {
        val b = Button(c)
        b.text = s
        b.isAllCaps = false
        b.setOnClickListener { onClick() }
        return b
    }
}
''')

w(K + "Prefs.kt", r'''
package com.salah.app

import android.content.Context
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

object Prefs {
    val KEYS = listOf("fajr", "dhuhr", "asr", "maghrib", "isha")
    val NAMES = mapOf(
        "fajr" to "الفجر",
        "dhuhr" to "الظهر",
        "asr" to "العصر",
        "maghrib" to "المغرب",
        "isha" to "العشاء"
    )

    private fun sp(c: Context) = c.getSharedPreferences("salah", Context.MODE_PRIVATE)

    fun lat(c: Context): Double = sp(c).getString("lat", "30.0444")!!.toDouble()
    fun lng(c: Context): Double = sp(c).getString("lng", "31.2357")!!.toDouble()
    fun hasLocation(c: Context): Boolean = sp(c).contains("lat")
    fun setLocation(c: Context, lat: Double, lng: Double) {
        sp(c).edit().putString("lat", lat.toString()).putString("lng", lng.toString()).apply()
    }

    fun blockedApps(c: Context): Set<String> =
        sp(c).getStringSet("blocked", emptySet())!!.toSet()

    fun setBlockedApps(c: Context, s: Set<String>) {
        sp(c).edit().putStringSet("blocked", HashSet(s)).apply()
    }

    fun blockEnabled(c: Context): Boolean = sp(c).getBoolean("block_on", true)
    fun setBlockEnabled(c: Context, b: Boolean) {
        sp(c).edit().putBoolean("block_on", b).apply()
    }

    fun pending(c: Context): List<String> {
        val s = sp(c).getString("pending", "")!!
        return if (s.isEmpty()) emptyList() else s.split(",")
    }

    private fun savePending(c: Context, l: List<String>) {
        sp(c).edit().putString("pending", l.joinToString(",")).apply()
    }

    fun addPending(c: Context, key: String) {
        val l = pending(c).toMutableList()
        if (!l.contains(key)) l.add(key)
        savePending(c, l)
    }

    fun clearPending(c: Context, keys: Collection<String>) {
        savePending(c, pending(c).filter { !keys.contains(it) })
    }

    fun blockingActive(c: Context): Boolean = blockEnabled(c) && pending(c).isNotEmpty()

    private fun today(): String = SimpleDateFormat("yyyy-MM-dd", Locale.US).format(Date())

    fun doneToday(c: Context): Set<String> =
        sp(c).getString("done_" + today(), "")!!.split(",").filter { it.isNotEmpty() }.toSet()

    fun markDone(c: Context, keys: Collection<String>) {
        val s = doneToday(c) + keys
        sp(c).edit().putString("done_" + today(), s.joinToString(",")).apply()
    }
}
''')

w(K + "PrayerTimes.kt", r'''
package com.salah.app

import java.util.Calendar
import java.util.TimeZone
import kotlin.math.abs
import kotlin.math.acos
import kotlin.math.asin
import kotlin.math.atan
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.floor
import kotlin.math.sin
import kotlin.math.tan

// حساب المواقيت بدون إنترنت. الطريقة المصرية: الفجر 19.5 والعشاء 17.5
object PrayerTimes {
    private fun rad(d: Double) = Math.toRadians(d)
    private fun dsin(d: Double) = sin(rad(d))
    private fun dcos(d: Double) = cos(rad(d))
    private fun dtan(d: Double) = tan(rad(d))
    private fun darcsin(x: Double) = Math.toDegrees(asin(x))
    private fun darccos(x: Double) = Math.toDegrees(acos(x))
    private fun darctan2(y: Double, x: Double) = Math.toDegrees(atan2(y, x))
    private fun darccot(x: Double) = Math.toDegrees(atan(1.0 / x))

    private fun fixAngle(a: Double): Double {
        var r = a % 360.0
        if (r < 0) r += 360.0
        return r
    }

    private fun fixHour(a: Double): Double {
        var r = a % 24.0
        if (r < 0) r += 24.0
        return r
    }

    private fun julian(y: Int, m: Int, d: Int): Double {
        var yy = y
        var mm = m
        if (mm <= 2) {
            yy -= 1
            mm += 12
        }
        val a = floor(yy / 100.0)
        val b = 2 - a + floor(a / 4.0)
        return floor(365.25 * (yy + 4716)) + floor(30.6001 * (mm + 1)) + d + b - 1524.5
    }

    private fun angleTime(angle: Double, noon: Double, lat: Double, decl: Double, before: Boolean): Double {
        val v = (-dsin(angle) - dsin(lat) * dsin(decl)) / (dcos(lat) * dcos(decl))
        val t = darccos(v.coerceIn(-1.0, 1.0)) / 15.0
        return if (before) noon - t else noon + t
    }

    fun compute(year: Int, month: Int, day: Int, lat: Double, lng: Double): Map<String, Long> {
        val cal = Calendar.getInstance()
        cal.clear()
        cal.set(year, month - 1, day, 12, 0, 0)
        val tz = TimeZone.getDefault().getOffset(cal.timeInMillis) / 3600000.0

        val utc = Calendar.getInstance(TimeZone.getTimeZone("UTC"))
        utc.clear()
        utc.set(year, month - 1, day, 0, 0, 0)
        val base = utc.timeInMillis

        val d = julian(year, month, day) + 0.5 - 2451545.0
        val g = fixAngle(357.529 + 0.98560028 * d)
        val q = fixAngle(280.459 + 0.98564736 * d)
        val l = fixAngle(q + 1.915 * dsin(g) + 0.020 * dsin(2 * g))
        val e = 23.439 - 0.00000036 * d
        val ra = fixHour(darctan2(dcos(e) * dsin(l), dcos(l)) / 15.0)
        val decl = darcsin(dsin(e) * dsin(l))
        var eqt = q / 15.0 - ra
        if (eqt > 12) eqt -= 24
        if (eqt < -12) eqt += 24

        val noon = 12 + tz - lng / 15.0 - eqt
        val fajr = angleTime(19.5, noon, lat, decl, true)
        val sunrise = angleTime(0.833, noon, lat, decl, true)
        val asrAngle = -darccot(1 + dtan(abs(lat - decl)))
        val asr = angleTime(asrAngle, noon, lat, decl, false)
        val maghrib = angleTime(0.833, noon, lat, decl, false)
        val isha = angleTime(17.5, noon, lat, decl, false)

        fun ms(t: Double): Long = base + ((t - tz) * 3600000.0).toLong()
        return mapOf(
            "fajr" to ms(fajr),
            "sunrise" to ms(sunrise),
            "dhuhr" to ms(noon),
            "asr" to ms(asr),
            "maghrib" to ms(maghrib),
            "isha" to ms(isha)
        )
    }

    fun today(lat: Double, lng: Double): Map<String, Long> {
        val c = Calendar.getInstance()
        return compute(c.get(Calendar.YEAR), c.get(Calendar.MONTH) + 1, c.get(Calendar.DAY_OF_MONTH), lat, lng)
    }

    fun next(lat: Double, lng: Double, now: Long): Pair<String, Long> {
        val c = Calendar.getInstance()
        for (i in 0..2) {
            val t = compute(c.get(Calendar.YEAR), c.get(Calendar.MONTH) + 1, c.get(Calendar.DAY_OF_MONTH), lat, lng)
            for (k in Prefs.KEYS) {
                val ms = t[k] ?: continue
                if (ms > now + 1000) return Pair(k, ms)
            }
            c.add(Calendar.DAY_OF_MONTH, 1)
        }
        return Pair("fajr", now + 3600000L)
    }

    fun current(lat: Double, lng: Double, now: Long): String {
        val t = today(lat, lng)
        var cur = "isha"
        for (k in Prefs.KEYS) {
            val ms = t[k] ?: continue
            if (ms <= now) cur = k
        }
        return cur
    }
}
''')

w(K + "Scheduler.kt", r'''
package com.salah.app

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent

object Scheduler {
    fun scheduleNext(c: Context) {
        val am = c.getSystemService(Context.ALARM_SERVICE) as AlarmManager
        val (key, at) = PrayerTimes.next(Prefs.lat(c), Prefs.lng(c), System.currentTimeMillis())
        val flags = PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        val op = PendingIntent.getBroadcast(
            c, 1001, Intent(c, AlarmReceiver::class.java).putExtra("key", key), flags
        )
        val show = PendingIntent.getActivity(c, 1002, Intent(c, MainActivity::class.java), flags)
        am.setAlarmClock(AlarmManager.AlarmClockInfo(at, show), op)
    }
}
''')

w(K + "AlarmReceiver.kt", r'''
package com.salah.app

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import androidx.core.content.ContextCompat

class AlarmReceiver : BroadcastReceiver() {
    override fun onReceive(c: Context, i: Intent) {
        val key = i.getStringExtra("key") ?: return
        Prefs.addPending(c, key)
        Scheduler.scheduleNext(c)
        try {
            ContextCompat.startForegroundService(c, Intent(c, PrayerService::class.java).putExtra("key", key))
        } catch (e: Exception) {
            PrayerService.notifyOnly(c, key)
        }
    }
}

class BootReceiver : BroadcastReceiver() {
    override fun onReceive(c: Context, i: Intent) {
        Scheduler.scheduleNext(c)
    }
}
''')

w(K + "PrayerService.kt", r'''
package com.salah.app

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.media.AudioAttributes
import android.media.MediaPlayer
import android.media.RingtoneManager
import android.net.Uri
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat

class PrayerService : Service() {
    companion object {
        @Volatile
        var ringing = false
        const val CH = "prayer_alarm"
        const val CH_FB = "prayer_fallback"

        fun notifyOnly(c: Context, key: String) {
            val nm = c.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            if (Build.VERSION.SDK_INT >= 26) {
                nm.createNotificationChannel(
                    NotificationChannel(CH_FB, "تنبيه الصلاة", NotificationManager.IMPORTANCE_HIGH)
                )
            }
            val pi = PendingIntent.getActivity(
                c, 2003, Intent(c, MainActivity::class.java),
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            val n = NotificationCompat.Builder(c, CH_FB)
                .setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
                .setContentTitle("حان الآن موعد صلاة " + (Prefs.NAMES[key] ?: ""))
                .setContentText("قوم صلّي")
                .setPriority(NotificationCompat.PRIORITY_MAX)
                .setDefaults(NotificationCompat.DEFAULT_ALL)
                .setAutoCancel(true)
                .setContentIntent(pi)
                .build()
            nm.notify(78, n)
        }
    }

    private var player: MediaPlayer? = null
    private val handler = Handler(Looper.getMainLooper())

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (intent?.action == "STOP") {
            stopSelf()
            return START_NOT_STICKY
        }
        val key = intent?.getStringExtra("key") ?: "fajr"
        val name = Prefs.NAMES[key] ?: ""
        ringing = true

        val nm = getSystemService(NOTIFICATION_SERVICE) as NotificationManager
        if (Build.VERSION.SDK_INT >= 26) {
            val ch = NotificationChannel(CH, "منبه الصلاة", NotificationManager.IMPORTANCE_HIGH)
            ch.setSound(null, null)
            nm.createNotificationChannel(ch)
        }

        val fl = PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        val open = Intent(this, MainActivity::class.java)
            .putExtra("alarm", true)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        val openPi = PendingIntent.getActivity(this, 2001, open, fl)
        val stopPi = PendingIntent.getService(
            this, 2002, Intent(this, PrayerService::class.java).setAction("STOP"), fl
        )

        val n: Notification = NotificationCompat.Builder(this, CH)
            .setSmallIcon(android.R.drawable.ic_lock_idle_alarm)
            .setContentTitle("حان الآن موعد صلاة $name")
            .setContentText("قوم صلّي، وبعدين قولّي في الشات إنك صليت")
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setFullScreenIntent(openPi, true)
            .setContentIntent(openPi)
            .addAction(0, "وقّف الصوت", stopPi)
            .setOngoing(true)
            .build()

        try {
            ServiceCompat.startForeground(this, 77, n, ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK)
        } catch (e: Exception) {
            notifyOnly(this, key)
        }

        val long = key == "fajr"
        startSound(long)
        handler.removeCallbacksAndMessages(null)
        handler.postDelayed({ stopSelf() }, if (long) 10 * 60000L else 90000L)
        return START_NOT_STICKY
    }

    private fun startSound(loop: Boolean) {
        stopSound()
        try {
            val res = resources.getIdentifier("adhan", "raw", packageName)
            val uri: Uri = if (res != 0) {
                Uri.parse("android.resource://$packageName/$res")
            } else {
                RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)
                    ?: RingtoneManager.getDefaultUri(RingtoneManager.TYPE_RINGTONE)
            }
            val p = MediaPlayer()
            p.setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_ALARM)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                    .build()
            )
            p.setDataSource(this, uri)
            p.isLooping = loop || res == 0
            p.prepare()
            p.start()
            player = p
        } catch (e: Exception) {
            player = null
        }
    }

    private fun stopSound() {
        try {
            player?.stop()
        } catch (e: Exception) {
        }
        player?.release()
        player = null
    }

    override fun onDestroy() {
        stopSound()
        handler.removeCallbacksAndMessages(null)
        ringing = false
        super.onDestroy()
    }
}
''')

w(K + "BlockerService.kt", r'''
package com.salah.app

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.view.accessibility.AccessibilityEvent

class BlockerService : AccessibilityService() {
    private var last = 0L

    override fun onAccessibilityEvent(e: AccessibilityEvent?) {
        if (e == null || e.eventType != AccessibilityEvent.TYPE_WINDOW_STATE_CHANGED) return
        val pkg = e.packageName?.toString() ?: return
        if (pkg == packageName) return
        if (!Prefs.blockingActive(this)) return
        if (!Prefs.blockedApps(this).contains(pkg)) return
        val now = System.currentTimeMillis()
        if (now - last < 800) return
        last = now
        performGlobalAction(GLOBAL_ACTION_HOME)
        val i = Intent(this, BlockActivity::class.java)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP)
        startActivity(i)
    }

    override fun onInterrupt() {}
}
''')

w(K + "BlockActivity.kt", r'''
package com.salah.app

import android.content.Intent
import android.graphics.Color
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import androidx.activity.ComponentActivity
import androidx.activity.addCallback

class BlockActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        onBackPressedDispatcher.addCallback(this) { goHome() }
        val l = LinearLayout(this)
        l.orientation = LinearLayout.VERTICAL
        l.gravity = Gravity.CENTER
        l.layoutDirection = View.LAYOUT_DIRECTION_RTL
        l.setBackgroundColor(Color.parseColor("#1B5E20"))
        val p = Ui.dp(this, 24)
        l.setPadding(p, p, p, p)
        val names = Prefs.pending(this).joinToString("، ") { Prefs.NAMES[it] ?: it }
        l.addView(Ui.text(this, "🔒 التطبيق ده مقفول", 26f, true, Color.WHITE))
        l.addView(
            Ui.text(
                this,
                "\nلسه عليك صلاة: $names\nصلّي الأول، وبعدين قولّي في الشات إنك صليت وصوّر السجادة.\n",
                18f, false, Color.WHITE
            )
        )
        l.addView(Ui.button(this, "افتح الشات") {
            startActivity(Intent(this, MainActivity::class.java))
            finish()
        })
        l.addView(Ui.button(this, "رجوع للشاشة الرئيسية") { goHome() })
        setContentView(l)
    }

    override fun onResume() {
        super.onResume()
        if (!Prefs.blockingActive(this)) finish()
    }

    private fun goHome() {
        startActivity(
            Intent(Intent.ACTION_MAIN)
                .addCategory(Intent.CATEGORY_HOME)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        )
        finish()
    }
}
''')

w(K + "ChatBot.kt", r'''
package com.salah.app

import android.content.Context
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

// شات بسيط شغال بدون إنترنت: ردود مكتوبة مسبقًا حسب كلامك
object ChatBot {
    data class Reply(val text: String, val askRug: Boolean = false, val keys: List<String> = emptyList())

    private val WORDS = mapOf(
        "fajr" to "فجر",
        "dhuhr" to "ظهر",
        "asr" to "عصر",
        "maghrib" to "مغرب",
        "isha" to "عشا"
    )

    private fun norm(s: String): String =
        s.replace(Regex("[\\u064B-\\u0652]"), "")
            .replace('أ', 'ا').replace('إ', 'ا').replace('آ', 'ا')
            .replace('ى', 'ي').replace('ة', 'ه').lowercase()

    private fun has(m: String, vararg w: String): Boolean = w.any { m.contains(it) }

    private fun reminder(c: Context): String {
        val p = Prefs.pending(c)
        if (p.isEmpty()) return ""
        return "\n\nلسه عليك: " + p.joinToString("، ") { Prefs.NAMES[it] ?: it } + " — قوم صلّي 🤲"
    }

    fun reply(c: Context, raw: String): Reply {
        val m = norm(raw)
        val pend = Prefs.pending(c)
        val denied = has(m, "ما صليت", "مصليت", "لم اصل", "مش مصلي")

        if (!denied && has(m, "صليت", "اديت", "خلصت صلاه")) {
            val named = WORDS.filter { m.contains(it.value) }.keys.toList()
            val keys = when {
                named.isNotEmpty() -> named
                pend.isNotEmpty() -> pend
                else -> listOf(PrayerTimes.current(Prefs.lat(c), Prefs.lng(c), System.currentTimeMillis()))
            }
            val names = keys.joinToString(" و") { Prefs.NAMES[it] ?: it }
            return Reply(
                "ما شاء الله، الله يتقبل منك 🤲\nعشان أتأكد وأفتحلك التطبيقات: صوّر سجادة الصلاة دلوقتي 📷 ($names)",
                true, keys
            )
        }

        if (denied || has(m, "مش عايز", "كسل", "تعبان", "نعسان", "بعدين", "مش قادر")) {
            return Reply(
                listOf(
                    "عارف إن الكسل صعب، بس دقايق قليلة وترتاح 💚 قوم توضا وصلّي.",
                    "الصلاة راحة للقلب. أول خطوة بس: قوم وهات الوضوء، والباقي هيمشي.",
                    "ما تأجلهاش! الصلاة على وقتها أحلى بكتير. أنا معاك، يلا قوم 🌙",
                    "إنت قدها. قوم صلّي ولما تخلص قولّي، وأنا فخور بيك."
                ).random() + reminder(c)
            )
        }

        if (has(m, "مواقيت", "الجايه", "الجاي", "امتي", "موعد", "الاذان")) {
            val (k, ms) = PrayerTimes.next(Prefs.lat(c), Prefs.lng(c), System.currentTimeMillis())
            val f = SimpleDateFormat("h:mm a", Locale("ar"))
            return Reply("الصلاة الجاية: ${Prefs.NAMES[k]} الساعة ${f.format(Date(ms))} 🕌" + reminder(c))
        }

        if (has(m, "سلام", "اهلا", "ازيك", "هاي", "صباح", "مساء")) {
            return Reply(
                listOf(
                    "وعليكم السلام ورحمة الله 🌙 إزيك؟ عامل إيه مع الصلاة النهاردة؟",
                    "أهلاً بيك! أنا هنا أفكّرك وأشجعك. صليت إيه النهاردة؟"
                ).random() + reminder(c)
            )
        }

        if (has(m, "شكرا", "جزاك")) {
            return Reply("وإياك، ربنا يثبتك ويتقبل منك 🤲")
        }

        return Reply(
            listOf(
                "أنا معاك 💚 لما تصلي قولّي «صليت» وصوّر السجادة.",
                "اسألني عن «الصلاة الجاية» وأقولك ميعادها، أو قولّي لو محتاج تشجيع.",
                "ربنا يعينك ويثبتك. فاكر؟ الصلاة على وقتها أحب الأعمال."
            ).random() + reminder(c)
        )
    }
}
''')

w(K + "MainActivity.kt", r'''
package com.salah.app

import android.Manifest
import android.app.AlertDialog
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.drawable.GradientDrawable
import android.location.Location
import android.location.LocationManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import android.view.Gravity
import android.view.View
import android.widget.Button
import android.widget.EditText
import android.widget.FrameLayout
import android.widget.LinearLayout
import android.widget.ScrollView
import android.widget.Switch
import android.widget.TextView
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.FileProvider
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.label.ImageLabeling
import com.google.mlkit.vision.label.defaults.ImageLabelerOptions
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class MainActivity : ComponentActivity() {
    private lateinit var content: FrameLayout
    private lateinit var chatView: View
    private lateinit var list: LinearLayout
    private lateinit var scroll: ScrollView
    private lateinit var banner: TextView
    private lateinit var stopBtn: Button
    private lateinit var input: EditText

    private var claimKeys: List<String> = emptyList()
    private var photoFile: File? = null
    private var page = 0

    private val rugWords = setOf(
        "rug", "carpet", "textile", "mat", "pattern", "tapestry",
        "linens", "floor", "flooring", "tile", "towel", "blanket"
    )

    private val takePicture = registerForActivityResult(ActivityResultContracts.TakePicture()) { ok ->
        if (ok) verifyRug() else bot("ما اتصورتش صورة. دوس على 📷 وجرّب تاني.")
    }

    private val permLauncher =
        registerForActivityResult(ActivityResultContracts.RequestMultiplePermissions()) {
            updateLocation()
            Scheduler.scheduleNext(this)
            if (page != 0) showPage(page)
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (Build.VERSION.SDK_INT >= 27 && intent.getBooleanExtra("alarm", false)) {
            setShowWhenLocked(true)
            setTurnScreenOn(true)
        }
        val root = LinearLayout(this)
        root.orientation = LinearLayout.VERTICAL
        root.layoutDirection = View.LAYOUT_DIRECTION_RTL
        root.setBackgroundColor(Color.WHITE)

        content = FrameLayout(this)
        root.addView(content, LinearLayout.LayoutParams(-1, 0, 1f))

        val bar = LinearLayout(this)
        bar.orientation = LinearLayout.HORIZONTAL
        listOf("الشات", "الصلوات", "الإعدادات").forEachIndexed { i, n ->
            bar.addView(Ui.button(this, n) { showPage(i) }, LinearLayout.LayoutParams(0, -2, 1f))
        }
        root.addView(bar, LinearLayout.LayoutParams(-1, -2))
        setContentView(root)

        chatView = buildChat()
        bot("السلام عليكم 🌙 أنا هنا أفكّرك بالصلاة وأتابع معاك. لما تصلي قولّي «صليت» وصوّر السجادة، وأنا أفتحلك التطبيقات.")

        val perms = mutableListOf(Manifest.permission.ACCESS_COARSE_LOCATION)
        if (Build.VERSION.SDK_INT >= 33) perms.add(Manifest.permission.POST_NOTIFICATIONS)
        val missing = perms.filter { checkSelfPermission(it) != PackageManager.PERMISSION_GRANTED }
        if (missing.isNotEmpty()) permLauncher.launch(missing.toTypedArray())

        updateLocation()
        Scheduler.scheduleNext(this)
        showPage(0)
    }

    override fun onResume() {
        super.onResume()
        refreshBanner()
        if (page != 0) showPage(page)
    }

    private fun showPage(p: Int) {
        page = p
        content.removeAllViews()
        val v = when (p) {
            0 -> chatView
            1 -> buildPrayers()
            else -> buildSettings()
        }
        content.addView(v, FrameLayout.LayoutParams(-1, -1))
        if (p == 0) refreshBanner()
    }

    // ---------------- الشات ----------------

    private fun buildChat(): View {
        val root = LinearLayout(this)
        root.orientation = LinearLayout.VERTICAL
        val pad = Ui.dp(this, 10)

        banner = Ui.text(this, "", 15f, true, Color.WHITE)
        banner.setBackgroundColor(Color.parseColor("#C62828"))
        banner.setPadding(pad, pad, pad, pad)
        banner.visibility = View.GONE
        root.addView(banner, LinearLayout.LayoutParams(-1, -2))

        stopBtn = Ui.button(this, "🔕 وقّف صوت المنبه") {
            stopService(Intent(this, PrayerService::class.java))
            stopBtn.visibility = View.GONE
        }
        stopBtn.visibility = View.GONE
        root.addView(stopBtn, LinearLayout.LayoutParams(-1, -2))

        scroll = ScrollView(this)
        list = LinearLayout(this)
        list.orientation = LinearLayout.VERTICAL
        list.setPadding(pad, pad, pad, pad)
        scroll.addView(list)
        root.addView(scroll, LinearLayout.LayoutParams(-1, 0, 1f))

        val row = LinearLayout(this)
        row.orientation = LinearLayout.HORIZONTAL
        input = EditText(this)
        input.hint = "اكتب هنا..."
        input.maxLines = 3
        row.addView(input, LinearLayout.LayoutParams(0, -2, 1f))
        row.addView(Ui.button(this, "📷") { startRugFlow() })
        row.addView(Ui.button(this, "إرسال") { onSend() })
        root.addView(row, LinearLayout.LayoutParams(-1, -2))
        return root
    }

    private fun addBubble(fromBot: Boolean, s: String) {
        val tv = TextView(this)
        tv.text = s
        tv.textSize = 16f
        tv.setTextColor(Color.BLACK)
        tv.maxWidth = Ui.dp(this, 290)
        val p = Ui.dp(this, 12)
        tv.setPadding(p, p, p, p)
        val bg = GradientDrawable()
        bg.cornerRadius = Ui.dp(this, 14).toFloat()
        bg.setColor(Color.parseColor(if (fromBot) "#DCEFD8" else "#E8E8E8"))
        tv.background = bg
        val lp = LinearLayout.LayoutParams(-2, -2)
        lp.gravity = if (fromBot) Gravity.START else Gravity.END
        lp.setMargins(0, Ui.dp(this, 4), 0, Ui.dp(this, 4))
        list.addView(tv, lp)
        scroll.post { scroll.fullScroll(View.FOCUS_DOWN) }
    }

    private fun bot(s: String) = addBubble(true, s)

    private fun refreshBanner() {
        val p = Prefs.pending(this)
        if (p.isEmpty()) {
            banner.visibility = View.GONE
        } else {
            var t = "⚠️ لسه عليك: " + p.joinToString("، ") { Prefs.NAMES[it] ?: it }
            if (Prefs.blockEnabled(this)) t += "\nالتطبيقات المحددة مقفولة لحد ما تصلي"
            banner.text = t
            banner.visibility = View.VISIBLE
        }
        stopBtn.visibility = if (PrayerService.ringing) View.VISIBLE else View.GONE
    }

    private fun onSend() {
        val t = input.text.toString().trim()
        if (t.isEmpty()) return
        input.setText("")
        stopService(Intent(this, PrayerService::class.java))
        addBubble(false, t)
        val r = ChatBot.reply(this, t)
        bot(r.text)
        if (r.askRug) {
            claimKeys = r.keys
            startCamera()
        }
        refreshBanner()
    }

    private fun defaultKeys(): List<String> {
        val p = Prefs.pending(this)
        return if (p.isNotEmpty()) p
        else listOf(PrayerTimes.current(Prefs.lat(this), Prefs.lng(this), System.currentTimeMillis()))
    }

    private fun startRugFlow() {
        if (claimKeys.isEmpty()) claimKeys = defaultKeys()
        bot("صوّر سجادة الصلاة 📷")
        startCamera()
    }

    private fun startCamera() {
        val dir = File(cacheDir, "images")
        dir.mkdirs()
        val f = File(dir, "rug.jpg")
        if (f.exists()) f.delete()
        photoFile = f
        val uri = FileProvider.getUriForFile(this, "$packageName.fileprovider", f)
        takePicture.launch(uri)
    }

    private fun verifyRug() {
        val f = photoFile ?: return
        bot("ثواني بتأكد من الصورة...")
        try {
            val image = InputImage.fromFilePath(this, Uri.fromFile(f))
            val labeler = ImageLabeling.getClient(
                ImageLabelerOptions.Builder().setConfidenceThreshold(0.4f).build()
            )
            labeler.process(image)
                .addOnSuccessListener { labels ->
                    val names = labels.map { it.text.lowercase() }
                    if (names.any { it in rugWords }) onVerified()
                    else bot("مش شايف سجادة صلاة في الصورة. صوّرها بوضوح وجرّب تاني 📷")
                }
                .addOnFailureListener {
                    bot("حصلت مشكلة في فحص الصورة، جرّب تصوّر تاني 📷")
                }
        } catch (e: Exception) {
            bot("حصلت مشكلة في قراءة الصورة، جرّب تاني 📷")
        }
    }

    private fun onVerified() {
        val keys = if (claimKeys.isEmpty()) defaultKeys() else claimKeys
        Prefs.markDone(this, keys)
        Prefs.clearPending(this, keys)
        claimKeys = emptyList()
        stopService(Intent(this, PrayerService::class.java))
        val names = keys.joinToString(" و") { Prefs.NAMES[it] ?: it }
        val left = Prefs.pending(this)
        if (left.isEmpty()) {
            bot("تقبّل الله ✅ اتسجلت صلاة $names. التطبيقات اتفتحت تاني 🔓 ثبّتك ربنا.")
        } else {
            bot("تقبّل الله ✅ اتسجلت $names.\nلسه عليك: " + left.joinToString("، ") { Prefs.NAMES[it] ?: it })
        }
        refreshBanner()
    }

    // ---------------- الصلوات ----------------

    private fun buildPrayers(): View {
        val sv = ScrollView(this)
        val l = LinearLayout(this)
        l.orientation = LinearLayout.VERTICAL
        val p = Ui.dp(this, 16)
        l.setPadding(p, p, p, p)
        sv.addView(l)

        val lat = Prefs.lat(this)
        val lng = Prefs.lng(this)
        val t = PrayerTimes.today(lat, lng)
        val now = System.currentTimeMillis()
        val done = Prefs.doneToday(this)
        val pend = Prefs.pending(this)
        val fmt = SimpleDateFormat("h:mm a", Locale("ar"))

        l.addView(Ui.text(this, "مواقيت اليوم", 22f, true))
        for (k in Prefs.KEYS) {
            val ms = t[k] ?: 0L
            val st = when {
                done.contains(k) -> "✅ صليت"
                pend.contains(k) -> "⚠️ مستني صلاتك"
                ms > now -> "⏳ لسه"
                else -> "—"
            }
            val row = Ui.text(this, "${Prefs.NAMES[k]}   ${fmt.format(Date(ms))}   $st", 18f)
            row.setPadding(0, Ui.dp(this, 12), 0, 0)
            l.addView(row)
        }
        val (nk, nms) = PrayerTimes.next(lat, lng, now)
        l.addView(Ui.text(this, "\nالصلاة الجاية: ${Prefs.NAMES[nk]} ${fmt.format(Date(nms))}", 16f, true))
        val where = if (Prefs.hasLocation(this)) "موقعك المحفوظ" else "القاهرة (لحد ما تسمح بالموقع)"
        l.addView(Ui.text(this, "\nالحساب بالطريقة المصرية، حسب: $where", 13f))
        return sv
    }

    // ---------------- الإعدادات ----------------

    private fun accEnabled(): Boolean {
        val s = Settings.Secure.getString(contentResolver, Settings.Secure.ENABLED_ACCESSIBILITY_SERVICES)
            ?: return false
        return s.contains(packageName)
    }

    private fun buildSettings(): View {
        val sv = ScrollView(this)
        val l = LinearLayout(this)
        l.orientation = LinearLayout.VERTICAL
        val p = Ui.dp(this, 16)
        l.setPadding(p, p, p, p)
        sv.addView(l)
        val pending = Prefs.pending(this).isNotEmpty()

        l.addView(Ui.text(this, "الإعدادات", 22f, true))

        l.addView(Ui.text(this, "\n1) خدمة القفل", 17f, true))
        l.addView(
            Ui.text(
                this,
                if (accEnabled()) "✅ شغالة" else "❌ مش مفعّلة. افتح الإعدادات وفعّل «صلاتي» من إمكانية الوصول."
            )
        )
        l.addView(Ui.button(this, "فتح إعدادات إمكانية الوصول") {
            startActivity(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
        })

        l.addView(Ui.text(this, "\n2) التطبيقات المقفولة (${Prefs.blockedApps(this).size})", 17f, true))
        val pick = Ui.button(this, "اختيار التطبيقات اللي تتقفل") { pickApps() }
        pick.isEnabled = !pending
        l.addView(pick)

        val sw = Switch(this)
        sw.text = if (pending) "القفل شغال لحد ما تصلي" else "تفعيل القفل لحد ما أصلي"
        sw.isChecked = Prefs.blockEnabled(this)
        sw.isEnabled = !pending
        sw.setOnCheckedChangeListener { _, b -> Prefs.setBlockEnabled(this, b) }
        l.addView(sw)

        l.addView(Ui.text(this, "\n3) المنبه والأذان", 17f, true))
        l.addView(Ui.button(this, "إلغاء توفير البطارية للتطبيق") {
            startActivity(Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS))
        })

        l.addView(Ui.text(this, "\n4) الموقع (لمواقيت دقيقة)", 17f, true))
        l.addView(Ui.button(this, "تحديث موقعي") {
            if (checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                permLauncher.launch(arrayOf(Manifest.permission.ACCESS_COARSE_LOCATION))
            } else {
                val ok = updateLocation()
                bot(if (ok) "اتحدّث موقعك ✅" else "مقدرتش أجيب موقعك. افتح خرائط جوجل مرة وجرّب تاني.")
                showPage(2)
            }
        })

        l.addView(Ui.text(this, "\n5) تجربة", 17f, true))
        l.addView(Ui.button(this, "تجربة المنبه والقفل (ظهر)") {
            sendBroadcast(Intent(this, AlarmReceiver::class.java).putExtra("key", "dhuhr"))
            showPage(0)
        })
        l.addView(Ui.text(this, "التجربة بتشغّل المنبه وتقفل التطبيقات لحد ما تقول «صليت» وتصوّر السجادة.", 13f))
        return sv
    }

    private fun pickApps() {
        val pm = packageManager
        val q = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        val skip = setOf(
            packageName, "com.android.settings", "com.android.dialer",
            "com.samsung.android.dialer", "com.google.android.dialer",
            "com.samsung.android.incallui", "com.android.emergency"
        )
        val apps = pm.queryIntentActivities(q, 0)
            .map { it.activityInfo.packageName to it.loadLabel(pm).toString() }
            .filter { !skip.contains(it.first) }
            .distinctBy { it.first }
            .sortedBy { it.second.lowercase() }
        val chosen = Prefs.blockedApps(this).toMutableSet()
        val checked = BooleanArray(apps.size) { chosen.contains(apps[it].first) }
        AlertDialog.Builder(this)
            .setTitle("اختار التطبيقات اللي تتقفل")
            .setMultiChoiceItems(apps.map { it.second }.toTypedArray(), checked) { _, which, isChecked ->
                if (isChecked) chosen.add(apps[which].first) else chosen.remove(apps[which].first)
            }
            .setPositiveButton("حفظ") { _, _ ->
                Prefs.setBlockedApps(this, chosen)
                showPage(2)
            }
            .setNegativeButton("إلغاء", null)
            .show()
    }

    private fun updateLocation(): Boolean {
        if (checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            return false
        }
        val lm = getSystemService(LOCATION_SERVICE) as LocationManager
        var best: Location? = null
        for (prov in lm.getProviders(true)) {
            val loc: Location? = try {
                lm.getLastKnownLocation(prov)
            } catch (e: SecurityException) {
                null
            }
            val b = best
            if (loc != null && (b == null || loc.time > b.time)) best = loc
        }
        val r = best ?: return false
        Prefs.setLocation(this, r.latitude, r.longitude)
        Scheduler.scheduleNext(this)
        return true
    }
}
''')
