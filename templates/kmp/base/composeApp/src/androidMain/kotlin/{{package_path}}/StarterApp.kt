package {{package_name}}

import android.app.Application
import {{package_name}}.di.sharedModules
import org.koin.android.ext.koin.androidContext
import org.koin.core.context.startKoin

class StarterApp : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            androidContext(this@StarterApp)
            modules(sharedModules)
        }
    }
}
