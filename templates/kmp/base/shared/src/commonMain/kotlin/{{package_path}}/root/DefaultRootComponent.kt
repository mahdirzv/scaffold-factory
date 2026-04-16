package {{package_name}}.root

import com.arkivanov.decompose.ComponentContext
import com.arkivanov.decompose.router.pages.ChildPages
import com.arkivanov.decompose.router.pages.Pages
import com.arkivanov.decompose.router.pages.PagesNavigation
import com.arkivanov.decompose.router.pages.childPages
import com.arkivanov.decompose.router.pages.select
import com.arkivanov.decompose.value.Value
import {{package_name}}.home.DefaultHomeComponent
import {{package_name}}.settings.DefaultSettingsComponent
import kotlinx.serialization.Serializable

class DefaultRootComponent(
    componentContext: ComponentContext,
) : RootComponent, ComponentContext by componentContext {

    private val navigation = PagesNavigation<TabConfig>()

    override val pages: Value<ChildPages<*, RootComponent.Tab>> =
        childPages(
            source = navigation,
            serializer = TabConfig.serializer(),
            initialPages = {
                Pages(
                    items = listOf(TabConfig.Home, TabConfig.Settings),
                    selectedIndex = 0,
                )
            },
            childFactory = ::child,
        )

    override fun selectTab(index: Int) {
        navigation.select(index = index)
    }

    private fun child(config: TabConfig, childComponentContext: ComponentContext): RootComponent.Tab =
        when (config) {
            is TabConfig.Home -> RootComponent.Tab.Home(
                DefaultHomeComponent(componentContext = childComponentContext)
            )

            is TabConfig.Settings -> RootComponent.Tab.Settings(
                DefaultSettingsComponent(componentContext = childComponentContext)
            )
        }

    @Serializable
    private sealed interface TabConfig {
        @Serializable
        data object Home : TabConfig

        @Serializable
        data object Settings : TabConfig
    }
}
