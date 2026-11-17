import os

K = "app/src/main/java/com/salah/app/"

# 1) شاشة القبلة
with open(K + "QiblaActivity.kt", "w", encoding="utf-8") as f:
    f.write(r'''package com.salah.app

import android.graphics.Color
import android.hardware.GeomagneticField
import android.hardware.Sensor
import android.hardware.SensorEvent
import android.hardware.SensorEventListener
import android.hardware.SensorManager
import android.os.Bundle
import android.view.Gravity
import android.view.View
import android.widget.LinearLayout
import android.widget.TextView
import androidx.activity.ComponentActivity
import kotlin.math.atan2
import kotlin.math.cos
import kotlin.math.roundToInt
import kotlin.math.sin

class QiblaActivity : ComponentActivity(), SensorEventListener {
    private lateinit var arrow: TextView
    private lateinit var info: TextView
    private var qibla = 0.0
    private var declination = 0f
    private var smooth = 0f
    private var first = true
    private var sm: SensorManager? = null

    private fun bearing(lat: Double, lng: Double): Double {
        val p1 = Math.toRadians(lat)
        val p2 = Math.toRadians(21.4225)
        val dl = Math.toRadians(39.8262 - lng)
        val y = sin(dl) * cos(p2)
        val x = cos(p1) * sin(p2) - sin(p1) * cos(p2) * cos(dl)
        return (Math.toDegrees(atan2(y, x)) + 360.0) % 360.0
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val lat = Prefs.lat(this)
        val lng = Prefs.lng(this)
        qibla = bearing(lat, lng)
        declination = GeomagneticField(lat.toFloat(), lng.toFloat(), 0f, System.currentTimeMillis()).declination

        val l = LinearLayout(this)
        l.orientation = LinearLayout.VERTICAL
        l.gravity = Gravity.CENTER_HORIZONTAL
        l.layoutDirection = View.LAYOUT_DIRECTION_RTL
        l.setBackgroundColor(Color.WHITE)
        val p = Ui.dp(this, 20)
        l.setPadding(p, p, p, p)

        arrow = Ui.text(this, "▲", 150f, true, Color.parseColor("#1B5E20"))
        arrow.gravity = Gravity.CENTER
        info = Ui.text(this, "", 14f)
        val where = if (Prefs.hasLocation(this)) "حسب موقعك" else "حسب القاهرة (اسمح بالموقع من الإعدادات)"

        l.addView(Ui.text(this, "🧭 اتجاه القبلة", 24f, true))
        l.addView(arrow, LinearLayout.LayoutParams(-1, Ui.dp(this, 260)))
        l.addView(Ui.text(this, "زاوية القبلة: ${qibla.roundToInt()}° من الشمال ($where)", 16f, true))
        l.addView(
            Ui.text(
                this,
                "\nامسك الموبايل مسطّح على كفّك، والسهم الأخضر يشاور على القبلة. ابعد عن المعادن والمغناطيس، ولو مش دقيق حرّك الموبايل على شكل 8.",
                13f
            )
        )
        l.addView(info)
        setContentView(l)
    }

    override fun onResume() {
        super.onResume()
        sm = getSystemService(SENSOR_SERVICE) as SensorManager
        val s = sm?.getDefaultSensor(Sensor.TYPE_ROTATION_VECTOR)
        if (s == null) {
            info.text = "الموبايل مفيهوش حساس اتجاه. استخدم الزاوية المكتوبة فوق مع أي بوصلة."
        } else {
            sm?.registerListener(this, s, SensorManager.SENSOR_DELAY_UI)
        }
    }

    override fun onPause() {
        super.onPause()
        sm?.unregisterListener(this)
    }

    override fun onSensorChanged(e: SensorEvent) {
        val r = FloatArray(9)
        val o = FloatArray(3)
        SensorManager.getRotationMatrixFromVector(r, e.values)
        SensorManager.getOrientation(r, o)
        var az = Math.toDegrees(o[0].toDouble()).toFloat() + declination
        az = (az + 360f) % 360f
        if (first) {
            smooth = az
            first = false
        } else {
            var d = az - smooth
            while (d > 180f) d -= 360f
            while (d < -180f) d += 360f
            smooth = (smooth + 0.15f * d + 360f) % 360f
        }
        arrow.rotation = (qibla.toFloat() - smooth + 360f) % 360f
    }

    override fun onAccuracyChanged(s: Sensor?, a: Int) {}
}
''')

# 2) تسجيل الشاشة في الـ Manifest
mp = "app/src/main/AndroidManifest.xml"
m = open(mp, encoding="utf-8").read()
assert "</application>" in m
m = m.replace(
    "</application>",
    '<activity android:name=".QiblaActivity" android:exported="false" '
    'android:screenOrientation="portrait"/>\n    </application>'
)
open(mp, "w", encoding="utf-8").write(m)

# 3) زرار القبلة في صفحة الصلوات
sp = K + "MainActivity.kt"
s = open(sp, encoding="utf-8").read()
a = r'''l.addView(Ui.text(this, "\nالحساب بالطريقة المصرية، حسب: $where", 13f))'''
assert a in s
s = s.replace(
    a,
    a + '''
        l.addView(Ui.button(this, "🧭 اتجاه القبلة") { startActivity(Intent(this, QiblaActivity::class.java)) })'''
)
open(sp, "w", encoding="utf-8").write(s)
