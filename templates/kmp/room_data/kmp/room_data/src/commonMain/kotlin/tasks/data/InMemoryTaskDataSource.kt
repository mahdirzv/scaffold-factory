package tasks.data

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import tasks.domain.Task

class InMemoryTaskDataSource : TaskLocalDataSource {
    private val mutableTasks = MutableStateFlow<List<Task>>(emptyList())
    override val tasks: StateFlow<List<Task>> = mutableTasks

    override fun getTask(id: String): Task? = mutableTasks.value.firstOrNull { it.id == id }

    override suspend fun upsert(task: Task) {
        val next = mutableTasks.value.toMutableList()
        val index = next.indexOfFirst { it.id == task.id }
        if (index >= 0) next[index] = task else next.add(task)
        mutableTasks.value = next
    }

    override suspend fun delete(taskId: String) {
        mutableTasks.value = mutableTasks.value.filterNot { it.id == taskId }
    }

    override suspend fun toggle(taskId: String) {
        mutableTasks.value = mutableTasks.value.map {
            if (it.id == taskId) it.copy(completed = !it.completed) else it
        }
    }
}
