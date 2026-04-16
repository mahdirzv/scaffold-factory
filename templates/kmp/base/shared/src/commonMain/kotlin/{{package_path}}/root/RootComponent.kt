package {{package_name}}.root

import com.arkivanov.decompose.router.pages.ChildPages
import com.arkivanov.decompose.value.Value
import {{package_name}}.home.HomeComponent
import {{package_name}}.settings.SettingsComponent

interface RootComponent {
    val pages: Value<ChildPages<*, Tab>>

    fun selectTab(index: Int)

    sealed class Tab {
        class Home(val component: HomeComponent) : Tab()
        class Settings(val component: SettingsComponent) : Tab()
    }
}
