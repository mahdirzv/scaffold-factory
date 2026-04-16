package {{package_name}}.home

import kotlinx.coroutines.flow.StateFlow

data class HomeUiState(
    val greeting: String = "",
)

interface HomeComponent {
    val uiState: StateFlow<HomeUiState>
}
