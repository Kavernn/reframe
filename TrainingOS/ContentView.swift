import SwiftUI
import Combine

// MARK: - Tab Bar Visibility (partagé via Environment)
class TabBarVisibility: ObservableObject {
    static let shared = TabBarVisibility()
    @Published var visible = true
}

struct ContentView: View {
    @StateObject private var api      = APIService.shared
    @StateObject private var network  = NetworkMonitor.shared
    @StateObject private var tabState = TabBarVisibility.shared
    @State private var selectedTab    = 0
    @State private var keyboardUp     = false

    private var showBar: Bool { tabState.visible && !keyboardUp }

    var body: some View {
        TabView(selection: $selectedTab) {
            DashboardView().tag(0)
            SeanceView().tag(1)
            HistoriqueView().tag(2)
            TimerView().tag(3)
            MoreView().tag(4)
        }
        .ignoresSafeArea(edges: .bottom)
        .onAppear { UITabBar.appearance().isHidden = true }
        // Floating pill — overlay garantit la priorité de hit-testing
        .overlay(alignment: .bottom) {
            FloatingTabBar(selected: $selectedTab)
                .padding(.bottom, safeAreaBottom + 8)
                .opacity(showBar ? 1 : 0)
                .offset(y: showBar ? 0 : 80)
                .animation(.spring(response: 0.3, dampingFraction: 0.8), value: showBar)
                .allowsHitTesting(showBar)
        }
        // Offline banner
        .overlay(alignment: .top) {
            if !network.isOnline {
                HStack(spacing: 6) {
                    Image(systemName: "wifi.slash")
                        .font(.system(size: 12, weight: .semibold))
                    Text("Hors-ligne — données en cache")
                        .font(.system(size: 12, weight: .medium))
                }
                .foregroundColor(.white)
                .frame(maxWidth: .infinity)
                .padding(.vertical, 6)
                .background(Color.orange.opacity(0.9))
                .allowsHitTesting(false)
            }
        }
        .environmentObject(tabState)
        .onReceive(NotificationCenter.default.publisher(for: UIResponder.keyboardWillShowNotification)) { _ in
            withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) { keyboardUp = true }
        }
        .onReceive(NotificationCenter.default.publisher(for: UIResponder.keyboardWillHideNotification)) { _ in
            withAnimation(.spring(response: 0.3, dampingFraction: 0.8)) { keyboardUp = false }
        }
    }

    private var safeAreaBottom: CGFloat {
        UIApplication.shared.connectedScenes
            .compactMap { $0 as? UIWindowScene }
            .first?.windows.first?.safeAreaInsets.bottom ?? 0
    }
}

// MARK: - Floating Pill Tab Bar
struct FloatingTabBar: View {
    @Binding var selected: Int
    @Namespace private var ns

    let tabs: [(String, String, Color)] = [
        ("house.fill",           "Accueil",    .orange),
        ("dumbbell.fill",        "Séance",     .orange),
        ("calendar",             "Historique", .orange),
        ("timer",                "Timer",      .orange),
        ("ellipsis.circle.fill", "Plus",       .orange),
    ]

    var body: some View {
        HStack(spacing: 0) {
            ForEach(tabs.indices, id: \.self) { i in
                let (icon, label, color) = tabs[i]
                let isSelected = selected == i

                Button {
                    selected = i
                } label: {
                    VStack(spacing: 3) {
                        ZStack {
                            if isSelected {
                                Capsule()
                                    .fill(color.opacity(0.2))
                                    .frame(width: 40, height: 26)
                                    .shadow(color: color.opacity(0.4), radius: 6)
                                    .matchedGeometryEffect(id: "pill", in: ns)
                            }
                            Image(systemName: icon)
                                .font(.system(size: 15, weight: isSelected ? .semibold : .regular))
                                .foregroundColor(isSelected ? color : .gray.opacity(0.5))
                                .scaleEffect(isSelected ? 1.1 : 1.0)
                                .animation(.spring(response: 0.3, dampingFraction: 0.7), value: isSelected)
                        }
                        .frame(width: 40, height: 26)

                        Text(label)
                            .font(.system(size: 9, weight: isSelected ? .semibold : .regular))
                            .foregroundColor(isSelected ? color : .gray.opacity(0.45))
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 10)
                }
                .buttonStyle(SpringButtonStyle(scale: 0.88))
            }
        }
        .padding(.horizontal, 12)
        .background(
            ZStack {
                RoundedRectangle(cornerRadius: 26)
                    .fill(Color(hex: "0e0e1c").opacity(0.95))
                RoundedRectangle(cornerRadius: 26)
                    .fill(
                        LinearGradient(
                            colors: [.white.opacity(0.06), .clear],
                            startPoint: .top, endPoint: .bottom
                        )
                    )
            }
            .overlay(
                RoundedRectangle(cornerRadius: 26)
                    .stroke(Color.white.opacity(0.08), lineWidth: 0.5)
            )
        )
        .shadow(color: .black.opacity(0.5), radius: 20, x: 0, y: 8)
        .padding(.horizontal, 20)
    }
}
