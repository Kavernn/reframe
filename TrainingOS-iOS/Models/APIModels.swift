import Foundation

// MARK: - Dashboard
struct DashboardData: Codable {
    let today: String
    let week: Int
    let todayDate: String
    let alreadyLoggedToday: Bool
    let schedule: [String: String]
    let sessions: [String: SessionEntry]
    let suggestions: [String: SuggestionEntry]
    let goals: [String: GoalProgress]
    let fullProgram: [String: [String: String]]
    let nutritionTotals: NutritionTotals
    let profile: UserProfile

    enum CodingKeys: String, CodingKey {
        case today, week
        case todayDate = "today_date"
        case alreadyLoggedToday = "already_logged_today"
        case schedule, sessions, suggestions, goals
        case fullProgram = "full_program"
        case nutritionTotals = "nutrition_totals"
        case profile
    }
}

struct SessionEntry: Codable {
    let exos: [String]?
    let rpe: Double?
    let comment: String?
    let loggedAt: String?

    enum CodingKeys: String, CodingKey {
        case exos, rpe, comment
        case loggedAt = "logged_at"
    }
}

struct SuggestionEntry: Codable {
    let weight: Double?
    let reps: String?
    let sets: String?
    let note: String?
}

struct GoalProgress: Codable {
    let current: Double
    let goal: Double
    let achieved: Bool
}

struct NutritionTotals: Codable {
    let calories: Double?
    let protein: Double?
    let carbs: Double?
    let fat: Double?
}

struct UserProfile: Codable {
    let name: String?
    let weight: Double?
    let height: Double?
    let photoUrl: String?

    enum CodingKeys: String, CodingKey {
        case name, weight, height
        case photoUrl = "photo_url"
    }
}

// MARK: - Seance
struct ExerciseLog: Codable, Identifiable {
    var id = UUID()
    let name: String
    var sets: [SetEntry]

    enum CodingKeys: String, CodingKey {
        case name, sets
    }
}

struct SetEntry: Codable, Identifiable {
    var id = UUID()
    var weight: Double
    var reps: Int

    enum CodingKeys: String, CodingKey {
        case weight, reps
    }
}

// MARK: - Historique
struct HistoriqueSession: Identifiable {
    let id: String // date string
    let date: String
    let entry: SessionEntry
}
