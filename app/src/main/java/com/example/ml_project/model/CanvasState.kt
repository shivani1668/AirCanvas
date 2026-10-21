package com.example.ml_project.model

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path

/**
 * Tool modes available on the Air Canvas toolbar.
 */
enum class CanvasTool {
    PEN,
    ERASER
}

/**
 * Represents a single stroke drawn on the canvas.
 */
data class DrawnPath(
    val path: Path,
    val color: Color,
    val strokeWidth: Float,
    val isEraser: Boolean = false
)

/**
 * Represents a solved mathematical equation result.
 */
data class SolvedEquation(
    val id: String = java.util.UUID.randomUUID().toString(),
    val timestamp: Long = System.currentTimeMillis(),
    val expression: String,
    val category: String,
    val solutionSteps: List<String>,
    val finalAnswer: String,
    val source: String = "AI Gemini" // or "Offline Math Engine"
)

/**
 * State for the Gemini API connection & Math Solver result.
 */
sealed interface SolverUiState {
    object Idle : SolverUiState
    object Loading : SolverUiState
    data class Success(val solvedEquation: SolvedEquation) : SolverUiState
    data class Error(val message: String) : SolverUiState
}
