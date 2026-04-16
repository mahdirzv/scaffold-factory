package auth.domain

import kotlinx.coroutines.flow.StateFlow

data class AuthState(
    val userId: String? = null,
    val signedIn: Boolean = false,
)

interface AuthRepository {
    val state: StateFlow<AuthState>
    suspend fun signIn(email: String, password: String): Result<String>
    suspend fun signUp(email: String, password: String): Result<String>
    suspend fun signOut()
    fun currentUserId(): String?
}
