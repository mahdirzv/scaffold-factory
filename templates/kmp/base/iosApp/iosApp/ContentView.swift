import SwiftUI
import Shared

struct RootView: View {
    let root: RootComponent

    @ObservedObject
    private var pagesObserver: ObservableValue<ChildPages<AnyObject, RootComponentTab>>

    init(root: RootComponent) {
        self.root = root
        self.pagesObserver = ObservableValue(root.pages)
    }

    var body: some View {
        let pages = pagesObserver.value
        let selectedIndex = Int(pages.selectedIndex)

        TabView(selection: Binding(
            get: { selectedIndex },
            set: { index in root.selectTab(index: Int32(index)) }
        )) {
            homeTabView(pages: pages)
                .tabItem {
                    Label("Home", systemImage: "house.fill")
                }
                .tag(0)

            settingsTabView(pages: pages)
                .tabItem {
                    Label("Settings", systemImage: "gearshape.fill")
                }
                .tag(1)
        }
    }

    @ViewBuilder
    private func homeTabView(pages: ChildPages<AnyObject, RootComponentTab>) -> some View {
        if let homeTab = pages.items.first?.instance as? RootComponentTab.Home {
            HomeView(component: homeTab.component)
        } else {
            Color.clear
        }
    }

    @ViewBuilder
    private func settingsTabView(pages: ChildPages<AnyObject, RootComponentTab>) -> some View {
        if pages.items.count > 1,
           let settingsTab = pages.items[1].instance as? RootComponentTab.Settings {
            SettingsView(component: settingsTab.component)
        } else {
            Color.clear
        }
    }
}

struct HomeView: View {
    let component: HomeComponent

    @ObservedObject
    private var stateObserver: FlowObserver<HomeUiState>

    init(component: HomeComponent) {
        self.component = component
        self.stateObserver = FlowObserver(
            flow: component.uiState,
            initial: HomeUiState(greeting: "")
        )
    }

    var body: some View {
        let state = stateObserver.value

        VStack(spacing: 16) {
            Text(state.greeting)
                .font(.title)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding()
    }
}

struct SettingsView: View {
    let component: SettingsComponent

    var body: some View {
        VStack(spacing: 16) {
            Text("Settings")
                .font(.title)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
        .padding()
    }
}
