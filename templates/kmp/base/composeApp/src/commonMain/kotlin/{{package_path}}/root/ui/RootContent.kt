package {{package_name}}.root.ui

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import com.arkivanov.decompose.extensions.compose.pages.ChildPages
import com.arkivanov.decompose.extensions.compose.subscribeAsState
import {{package_name}}.home.ui.HomeScreen
import {{package_name}}.root.RootComponent
import {{package_name}}.settings.ui.SettingsScreen

@Composable
fun RootContent(component: RootComponent, modifier: Modifier = Modifier) {
    val pagesState by component.pages.subscribeAsState()
    val selectedIndex = pagesState.selectedIndex

    Scaffold(
        modifier = modifier,
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = selectedIndex == 0,
                    onClick = { component.selectTab(0) },
                    icon = { Icon(Icons.Default.Home, contentDescription = "Home") },
                    label = { Text("Home") },
                )
                NavigationBarItem(
                    selected = selectedIndex == 1,
                    onClick = { component.selectTab(1) },
                    icon = { Icon(Icons.Default.Settings, contentDescription = "Settings") },
                    label = { Text("Settings") },
                )
            }
        },
    ) { innerPadding ->
        ChildPages(
            pages = component.pages,
            onPageSelected = component::selectTab,
        ) { _, tab ->
            when (tab) {
                is RootComponent.Tab.Home -> HomeScreen(
                    component = tab.component,
                    modifier = Modifier.padding(innerPadding),
                )
                is RootComponent.Tab.Settings -> SettingsScreen(
                    component = tab.component,
                    modifier = Modifier.padding(innerPadding),
                )
            }
        }
    }
}
