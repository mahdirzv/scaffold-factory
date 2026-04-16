package auth.di

import auth.data.NoOpAuthRepository
import auth.domain.AuthRepository
import org.koin.dsl.module

val authModule = module {
    single<AuthRepository> { NoOpAuthRepository() }
}
