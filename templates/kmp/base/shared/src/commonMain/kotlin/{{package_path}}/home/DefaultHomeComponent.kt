package {{package_name}}.home

import com.arkivanov.decompose.ComponentContext
import {{package_name}}.getPlatform
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

class DefaultHomeComponent(
    componentContext: ComponentContext,
) : HomeComponent, ComponentContext by componentContext {

    override val uiState: StateFlow<HomeUiState> = MutableStateFlow(
        HomeUiState(greeting = "Hello from ${getPlatform().name}")
    ).asStateFlow()
}
