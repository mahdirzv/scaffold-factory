package {{package_name}}.di

import com.arkivanov.decompose.ComponentContext
import {{package_name}}.root.DefaultRootComponent
import {{package_name}}.root.RootComponent
import org.koin.core.component.KoinComponent
import org.koin.core.context.startKoin

fun initKoin() {
    startKoin {
        modules(sharedModules)
    }
}

object KoinHelper : KoinComponent {
    fun createRootComponent(componentContext: ComponentContext): RootComponent =
        DefaultRootComponent(componentContext = componentContext)
}
