import Foundation
import Combine

class APIService: ObservableObject {
    static let shared = APIService()

    private let baseURL = "https://training-os-rho.vercel.app"

    @Published var dashboard: DashboardData?
    @Published var isLoading = false
    @Published var error: String?

    private init() {}

    func fetchDashboard() async {
        await MainActor.run { isLoading = true; error = nil }
        do {
            let url = URL(string: "\(baseURL)/api/dashboard")!
            let (data, _) = try await URLSession.shared.data(from: url)
            let decoded = try JSONDecoder().decode(DashboardData.self, from: data)
            await MainActor.run {
                self.dashboard = decoded
                self.isLoading = false
            }
        } catch {
            await MainActor.run {
                self.error = error.localizedDescription
                self.isLoading = false
            }
        }
    }

    func logSession(exos: [String], rpe: Double, comment: String) async throws {
        let url = URL(string: "\(baseURL)/api/log_session")!
        var req = URLRequest(url: url)
        req.httpMethod = "POST"
        req.setValue("application/json", forHTTPHeaderField: "Content-Type")
        let body: [String: Any] = [
            "exos": exos,
            "rpe": rpe,
            "comment": comment
        ]
        req.httpBody = try JSONSerialization.data(withJSONObject: body)
        let (_, _) = try await URLSession.shared.data(for: req)
    }
}
