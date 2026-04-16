package ui.theme

import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.ui.graphics.Color

private val PrimaryLight = Color(0xFF1A73E8)
private val OnPrimaryLight = Color(0xFFFFFFFF)
private val PrimaryContainerLight = Color(0xFFD3E3FD)
private val OnPrimaryContainerLight = Color(0xFF041E49)
private val SecondaryLight = Color(0xFF5F6368)
private val OnSecondaryLight = Color(0xFFFFFFFF)
private val SecondaryContainerLight = Color(0xFFE8EAED)
private val OnSecondaryContainerLight = Color(0xFF1F1F1F)
private val BackgroundLight = Color(0xFFFAFAFA)
private val OnBackgroundLight = Color(0xFF1F1F1F)
private val SurfaceLight = Color(0xFFFFFFFF)
private val OnSurfaceLight = Color(0xFF1F1F1F)
private val ErrorLight = Color(0xFFD93025)
private val OnErrorLight = Color(0xFFFFFFFF)

private val PrimaryDark = Color(0xFF8AB4F8)
private val OnPrimaryDark = Color(0xFF041E49)
private val PrimaryContainerDark = Color(0xFF1A73E8)
private val OnPrimaryContainerDark = Color(0xFFD3E3FD)
private val SecondaryDark = Color(0xFFBDC1C6)
private val OnSecondaryDark = Color(0xFF1F1F1F)
private val SecondaryContainerDark = Color(0xFF3C4043)
private val OnSecondaryContainerDark = Color(0xFFE8EAED)
private val BackgroundDark = Color(0xFF1F1F1F)
private val OnBackgroundDark = Color(0xFFE8EAED)
private val SurfaceDark = Color(0xFF282828)
private val OnSurfaceDark = Color(0xFFE8EAED)
private val ErrorDark = Color(0xFFF28B82)
private val OnErrorDark = Color(0xFF1F1F1F)

val LightColorScheme = lightColorScheme(
    primary = PrimaryLight,
    onPrimary = OnPrimaryLight,
    primaryContainer = PrimaryContainerLight,
    onPrimaryContainer = OnPrimaryContainerLight,
    secondary = SecondaryLight,
    onSecondary = OnSecondaryLight,
    secondaryContainer = SecondaryContainerLight,
    onSecondaryContainer = OnSecondaryContainerLight,
    background = BackgroundLight,
    onBackground = OnBackgroundLight,
    surface = SurfaceLight,
    onSurface = OnSurfaceLight,
    error = ErrorLight,
    onError = OnErrorLight,
)

val DarkColorScheme = darkColorScheme(
    primary = PrimaryDark,
    onPrimary = OnPrimaryDark,
    primaryContainer = PrimaryContainerDark,
    onPrimaryContainer = OnPrimaryContainerDark,
    secondary = SecondaryDark,
    onSecondary = OnSecondaryDark,
    secondaryContainer = SecondaryContainerDark,
    onSecondaryContainer = OnSecondaryContainerDark,
    background = BackgroundDark,
    onBackground = OnBackgroundDark,
    surface = SurfaceDark,
    onSurface = OnSurfaceDark,
    error = ErrorDark,
    onError = OnErrorDark,
)
