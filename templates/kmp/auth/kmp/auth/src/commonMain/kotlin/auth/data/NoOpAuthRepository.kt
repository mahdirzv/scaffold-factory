package auth.data

import auth.domain.AuthRepository
import auth.domain.AuthState
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow

class NoOpAuthRepository : AuthRepository {
    private val mutableState = MutableStateFlow(AuthState())
    override val state: StateFlow<AuthState> = mutableState

    override suspend fun signIn(email: String, password: String): Result<String> {
        val userId = email.substringBefore('@').ifBlank { "guest" }
        mutableState.value = AuthState(userId = userId, signedIn = true)
        return Result.success(userId)
    }

    override suspend fun signUp(email: String, password: String): Result<String> {
        val userId = email.substringBefore('@').ifBlank { "guest" }
        mutableState.value = AuthState(userId = userId, signedIn = true)
        return Result.success(userId)
    }

    override suspend fun signOut() {
        mutableState.value = AuthState()
    }

    override fun currentUserId(): String? = mutableState.value.userId
}
