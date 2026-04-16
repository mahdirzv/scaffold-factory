import SwiftUI
import Shared

class ObservableValue<T: AnyObject>: ObservableObject {
    @Published var value: T

    private var cancellation: Cancellation?

    init(_ value: Value<T>) {
        self.value = value.value
        cancellation = value.subscribe { [weak self] newValue in
            self?.value = newValue
        }
    }

    deinit {
        cancellation?.cancel()
    }
}

@MainActor
class FlowObserver<T>: ObservableObject {
    @Published var value: T

    init(flow: SkieSwiftStateFlow<T>, initial: T) {
        self.value = initial
        Task { [weak self] in
            for await newValue in flow {
                self?.value = newValue
            }
        }
    }
}
