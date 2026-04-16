import SwiftUI
import Shared

@main
struct iOSApp: App {
    private let root: RootComponent

    init() {
        KoinIOSKt.doInitKoin()
        let lifecycle = LifecycleRegistryKt.LifecycleRegistry()
        let componentContext = DefaultComponentContext(lifecycle: lifecycle)
        root = KoinHelper.shared.createRootComponent(componentContext: componentContext)
    }

    var body: some Scene {
        WindowGroup {
            RootView(root: root)
        }
    }
}
