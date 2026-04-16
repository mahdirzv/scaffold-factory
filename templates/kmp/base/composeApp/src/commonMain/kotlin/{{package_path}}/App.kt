package {{package_name}}

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import {{package_name}}.root.RootComponent
import {{package_name}}.root.ui.RootContent
import {{package_name}}.ui.theme.AppTheme

@Composable
fun App(rootComponent: RootComponent) {
    AppTheme {
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background,
        ) {
            RootContent(component = rootComponent)
        }
    }
}
