package tasks.data

import kotlinx.coroutines.flow.StateFlow
import tasks.domain.Task

interface TaskLocalDataSource {
    val tasks: StateFlow<List<Task>>
    fun getTask(id: String): Task?
    suspend fun upsert(task: Task)
    suspend fun delete(taskId: String)
    suspend fun toggle(taskId: String)
}
