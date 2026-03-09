import SwiftUI

struct ContentView: View {
    @StateObject private var api = APIService.shared
    @StateObject private var network = NetworkMonitor.shared
    @State private var selectedTab = 0

    var body: some View {
        ZStack(alignment: .bottom) {
            // Offline banner
            if !network.isOnline {
                VStack(spacing: 0) {
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
                    Spacer()
                }
                .zIndex(1)
            }

            // Page content
            Group {
                switch selectedTab {
                case 0: DashboardView()
                case 1: SeanceView()
                case 2: HistoriqueView()
                case 3: TimerView()
                default: MoreView()
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)

            // Custom Tab Bar
            CustomTabBar(selected: $selectedTab)
        }
        .ignoresSafeArea(edges: .bottom)
    }
}

struct CustomTabBar: View {
    @Binding var selected: Int

    let tabs: [(String, String)] = [
        ("house.fill",          "Accueil"),
        ("dumbbell.fill",       "Séance"),
        ("calendar",            "Historique"),
        ("timer",               "Timer"),
        ("ellipsis.circle.fill","Plus"),
    ]

    var body: some View {
        HStack(spacing: 0) {
            ForEach(tabs.indices, id: \.self) { i in
                let (icon, label) = tabs[i]
                let isSelected = selected == i

                Button {
                    withAnimation(.spring(response: 0.35, dampingFraction: 0.7)) {
                        selected = i
                    }
                } label: {
                    VStack(spacing: 4) {
                        ZStack {
                            if isSelected {
                                Capsule()
                                    .fill(Color.orange.opacity(0.18))
                                    .frame(width: 44, height: 30)
                                    .shadow(color: .orange.opacity(0.3), radius: 8)
                                    .matchedGeometryEffect(id: "tabBG", in: tabNamespace)
                            }
                            Image(systemName: icon)
                                .font(.system(size: isSelected ? 17 : 16, weight: isSelected ? .semibold : .regular))
                                .foregroundColor(isSelected ? .orange : .gray.opacity(0.6))
                                .scaleEffect(isSelected ? 1.1 : 1.0)
                                .animation(.spring(response: 0.3, dampingFraction: 0.7), value: isSelected)
                        }
                        .frame(width: 44, height: 30)

                        Text(label)
                            .font(.system(size: 9, weight: isSelected ? .semibold : .regular))
                            .foregroundColor(isSelected ? .orange : .gray.opacity(0.5))
                            .scaleEffect(isSelected ? 1.05 : 1.0)
                            .animation(.spring(response: 0.3, dampingFraction: 0.7), value: isSelected)
                    }
                    .frame(maxWidth: .infinity)
                    .padding(.top, 10)
                    .padding(.bottom, 6)
                }
                .buttonStyle(SpringButtonStyle(scale: 0.92))
            }
        }
        .background(
            ZStack {
                Rectangle()
                    .fill(Color(hex: "0c0c18"))
                Rectangle()
                    .fill(
                        LinearGradient(
                            colors: [.white.opacity(0.05), .clear],
                            startPoint: .top,
                            endPoint: .bottom
                        )
                    )
            }
            .overlay(
                Rectangle()
                    .fill(Color.white.opacity(0.07))
                    .frame(height: 0.5),
                alignment: .top
            )
        )
        .shadow(color: .black.opacity(0.5), radius: 20, x: 0, y: -4)
        .padding(.bottom, safeAreaBottom)
    }

    @Namespace private var tabNamespace

    private var safeAreaBottom: CGFloat {
        UIApplication.shared.connectedScenes
            .compactMap { $0 as? UIWindowScene }
            .first?.windows.first?.safeAreaInsets.bottom ?? 0
    }
}
