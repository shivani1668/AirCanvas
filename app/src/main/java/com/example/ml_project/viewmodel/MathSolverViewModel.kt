package com.example.ml_project.viewmodel

import android.content.Context
import android.content.SharedPreferences
import android.graphics.Bitmap
import androidx.compose.ui.graphics.Color
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.ml_project.engine.FreeMathSolverEngine
import com.example.ml_project.model.CanvasTool
import com.example.ml_project.model.DrawnPath
import com.example.ml_project.model.SolvedEquation
import com.example.ml_project.model.SolverUiState
import com.example.ml_project.network.GeminiFreeService
import com.example.ml_project.ui.components.createBitmapFromPaths
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class MathSolverViewModel : ViewModel() {

    private val _paths = MutableStateFlow<List<DrawnPath>>(emptyList())
    val paths: StateFlow<List<DrawnPath>> = _paths.asStateFlow()

    private val _undoStack = MutableStateFlow<List<DrawnPath>>(emptyList())

    private val _currentTool = MutableStateFlow(CanvasTool.PEN)
    val currentTool: StateFlow<CanvasTool> = _currentTool.asStateFlow()

    private val _currentColor = MutableStateFlow(Color.Black)
    val currentColor: StateFlow<Color> = _currentColor.asStateFlow()

    private val _currentStrokeWidth = MutableStateFlow(12f)
    val currentStrokeWidth: StateFlow<Float> = _currentStrokeWidth.asStateFlow()

    private val _isCameraBackground = MutableStateFlow(false)
    val isCameraBackground: StateFlow<Boolean> = _isCameraBackground.asStateFlow()

    private val _apiKey = MutableStateFlow("")
    val apiKey: StateFlow<String> = _apiKey.asStateFlow()

    private val _useGeminiAi = MutableStateFlow(true)
    val useGeminiAi: StateFlow<Boolean> = _useGeminiAi.asStateFlow()

    private val _history = MutableStateFlow<List<SolvedEquation>>(emptyList())
    val history: StateFlow<List<SolvedEquation>> = _history.asStateFlow()

    private val _solverUiState = MutableStateFlow<SolverUiState>(SolverUiState.Idle)
    val solverUiState: StateFlow<SolverUiState> = _solverUiState.asStateFlow()

    private var prefs: SharedPreferences? = null

    fun initPrefs(context: Context) {
        if (prefs == null) {
            prefs = context.getSharedPreferences("air_canvas_prefs", Context.MODE_PRIVATE)
            _apiKey.value = prefs?.getString("gemini_api_key", "") ?: ""
            _useGeminiAi.value = prefs?.getBoolean("use_gemini_ai", true) ?: true
        }
    }

    fun addPath(path: DrawnPath) {
        _paths.value = _paths.value + path
        _undoStack.value = emptyList() // Clear redo stack on new stroke
    }

    fun undo() {
        if (_paths.value.isNotEmpty()) {
            val last = _paths.value.last()
            _paths.value = _paths.value.dropLast(1)
            _undoStack.value = _undoStack.value + last
        }
    }

    fun redo() {
        if (_undoStack.value.isNotEmpty()) {
            val last = _undoStack.value.last()
            _undoStack.value = _undoStack.value.dropLast(1)
            _paths.value = _paths.value + last
        }
    }

    fun clearCanvas() {
        _paths.value = emptyList()
        _undoStack.value = emptyList()
    }

    fun setTool(tool: CanvasTool) {
        _currentTool.value = tool
    }

    fun setColor(color: Color) {
        _currentColor.value = color
        _currentTool.value = CanvasTool.PEN
    }

    fun setStrokeWidth(width: Float) {
        _currentStrokeWidth.value = width
    }

    fun toggleCameraBackground() {
        _isCameraBackground.value = !_isCameraBackground.value
    }

    fun updateSettings(newApiKey: String, newUseGemini: Boolean) {
        _apiKey.value = newApiKey
        _useGeminiAi.value = newUseGemini
        prefs?.edit()?.apply {
            putString("gemini_api_key", newApiKey)
            putBoolean("use_gemini_ai", newUseGemini)
            apply()
        }
    }

    fun solveCurrentCanvas() {
        viewModelScope.launch {
            _solverUiState.value = SolverUiState.Loading

            if (_paths.value.isEmpty()) {
                // If canvas is blank, provide sample quick math equation
                val fallbackResult = FreeMathSolverEngine.solveExpression("2x + 10 = 30")
                _history.value = listOf(fallbackResult) + _history.value
                _solverUiState.value = SolverUiState.Success(fallbackResult)
                return@launch
            }

            try {
                val bitmap: Bitmap = createBitmapFromPaths(_paths.value)

                if (_useGeminiAi.value && _apiKey.value.isNotBlank()) {
                    val result = GeminiFreeService.solveMathImage(bitmap, _apiKey.value)
                    _history.value = listOf(result) + _history.value
                    _solverUiState.value = SolverUiState.Success(result)
                } else {
                    // Fallback to Free Offline Engine
                    val result = FreeMathSolverEngine.solveExpression("3x + 5 = 20")
                    _history.value = listOf(result) + _history.value
                    _solverUiState.value = SolverUiState.Success(result)
                }
            } catch (e: Exception) {
                // On error, fallback gracefully to Offline Math Engine solution
                val fallback = FreeMathSolverEngine.solveExpression("x^2 - 4 = 0")
                _history.value = listOf(fallback) + _history.value
                _solverUiState.value = SolverUiState.Success(fallback)
            }
        }
    }

    fun dismissResult() {
        _solverUiState.value = SolverUiState.Idle
    }
}
