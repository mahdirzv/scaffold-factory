package tasks.di

import org.koin.dsl.module
import tasks.data.DefaultTaskRepository
import tasks.data.InMemoryTaskDataSource
import tasks.data.TaskLocalDataSource
import tasks.data.TaskRepository

val dataModule = module {
    single<TaskLocalDataSource> { InMemoryTaskDataSource() }
    single<TaskRepository> { DefaultTaskRepository(get()) }
}
