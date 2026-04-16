package tasks.data

import kotlinx.coroutines.flow.StateFlow
import tasks.domain.Task

class DefaultTaskRepository(
    private val localDataSource: TaskLocalDataSource,
) : TaskRepository {
    override val tasks: StateFlow<List<Task>> = localDataSource.tasks

    override fun getTask(id: String): Task? = localDataSource.getTask(id)

    override suspend fun addTask(task: Task) {
        localDataSource.upsert(task)
    }

    override suspend fun removeTask(taskId: String) {
        localDataSource.delete(taskId)
    }

    override suspend fun toggleTask(taskId: String) {
        localDataSource.toggle(taskId)
    }
}
