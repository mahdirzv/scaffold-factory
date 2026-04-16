package tasks.data

import kotlinx.coroutines.flow.StateFlow
import tasks.domain.Task

interface TaskRepository {
    val tasks: StateFlow<List<Task>>
    fun getTask(id: String): Task?
    suspend fun addTask(task: Task)
    suspend fun removeTask(taskId: String)
    suspend fun toggleTask(taskId: String)
}
