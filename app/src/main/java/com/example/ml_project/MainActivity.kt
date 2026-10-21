package com.example.ml_project

import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Brush
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.History
import androidx.compose.material.icons.filled.Redo
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material.icons.filled.Undo
import androidx.compose.material.icons.filled.Videocam
import androidx.compose.material.icons.filled.VideocamOff
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.ml_project.model.CanvasTool
import com.example.ml_project.model.SolverUiState
import com.example.ml_project.ui.components.CameraPreview
import com.example.ml_project.ui.components.DrawingCanvas
import com.example.ml_project.ui.components.MathResultSheet
import com.example.ml_project.ui.components.SettingsDialog
import com.example.ml_project.ui.theme.ML_projectTheme
import com.example.ml_project.viewmodel.MathSolverViewModel

class MainActivity : ComponentActivity() {

    private val viewModel: MathSolverViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        setContent {
            ML_projectTheme {
                AirCanvasApp(viewModel = viewModel)
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AirCanvasApp(viewModel: MathSolverViewModel) {
    val context = LocalContext.current

    LaunchedEffect(Unit) {
        viewModel.initPrefs(context)
    }

    val paths by viewModel.paths.collectAsState()
    val currentTool by viewModel.currentTool.collectAsState()
    val currentColor by viewModel.currentColor.collectAsState()
    val currentStrokeWidth by viewModel.currentStrokeWidth.collectAsState()
    val isCameraBackground by viewModel.isCameraBackground.collectAsState()
    val apiKey by viewModel.apiKey.collectAsState()
    val useGeminiAi by viewModel.useGeminiAi.collectAsState()
    val history by viewModel.history.collectAsState()
    val solverUiState by viewModel.solverUiState.collectAsState()

    var showSettingsDialog by remember { mutableStateOf(false) }
    var showHistoryDialog by remember { mutableStateOf(false) }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text(
                            text = "Air Canvas",
                            style = MaterialTheme.typography.titleLarge,
                            fontWeight = FontWeight.Bold
                        )
                        Text(
                            text = "Draw math, let AI solve!",
                            style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                },
                actions = {
                    // Camera Toggle
                    IconButton(
                        onClick = { viewModel.toggleCameraBackground() }
                    ) {
                        Icon(
                            imageVector = if (isCameraBackground) Icons.Default.Videocam else Icons.Default.VideocamOff,
                            contentDescription = "Toggle Air Camera Mode",
                            tint = if (isCameraBackground) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface
                        )
                    }

                    // History
                    IconButton(onClick = { showHistoryDialog = true }) {
                        Icon(
                            imageVector = Icons.Default.History,
                            contentDescription = "History"
                        )
                    }

                    // Settings
                    IconButton(onClick = { showSettingsDialog = true }) {
                        Icon(
                            imageVector = Icons.Default.Settings,
                            contentDescription = "Settings"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surfaceContainer
                )
            )
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            // Background: Live CameraPreview (Air Mode) or Canvas White
            if (isCameraBackground) {
                CameraPreview(modifier = Modifier.fillMaxSize())
            }

            // Interactive Drawing Canvas Overlay
            DrawingCanvas(
                paths = paths,
                currentTool = currentTool,
                currentColor = currentColor,
                currentStrokeWidth = currentStrokeWidth,
                isCameraBackground = isCameraBackground,
                onPathAdded = { viewModel.addPath(it) },
                modifier = Modifier.fillMaxSize()
            )

            // Bottom Floating Controls Toolbar
            Column(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .fillMaxWidth()
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Brush Palette & Controls Card
                Surface(
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(20.dp),
                    color = MaterialTheme.colorScheme.surfaceContainerHigh.copy(alpha = 0.95f),
                    shadowElevation = 8.dp
                ) {
                    Column(
                        modifier = Modifier.padding(12.dp),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        // Palette & Tools Row
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            // Pen / Eraser Tool
                            Row {
                                IconButton(
                                    onClick = { viewModel.setTool(CanvasTool.PEN) },
                                    colors = IconButtonDefaults.iconButtonColors(
                                        containerColor = if (currentTool == CanvasTool.PEN) MaterialTheme.colorScheme.primaryContainer else Color.Transparent
                                    )
                                ) {
                                    Icon(Icons.Default.Brush, contentDescription = "Pen")
                                }

                                IconButton(
                                    onClick = { viewModel.setTool(CanvasTool.ERASER) },
                                    colors = IconButtonDefaults.iconButtonColors(
                                        containerColor = if (currentTool == CanvasTool.ERASER) MaterialTheme.colorScheme.primaryContainer else Color.Transparent
                                    )
                                ) {
                                    Icon(Icons.Default.Clear, contentDescription = "Eraser")
                                }
                            }

                            // Undo / Redo / Clear
                            Row {
                                IconButton(onClick = { viewModel.undo() }) {
                                    Icon(Icons.Default.Undo, contentDescription = "Undo")
                                }
                                IconButton(onClick = { viewModel.redo() }) {
                                    Icon(Icons.Default.Redo, contentDescription = "Redo")
                                }
                                IconButton(onClick = { viewModel.clearCanvas() }) {
                                    Icon(Icons.Default.Delete, contentDescription = "Clear Canvas")
                                }
                            }
                        }

                        // Colors Palette
                        if (currentTool == CanvasTool.PEN) {
                            Spacer(modifier = Modifier.height(8.dp))
                            val colors = listOf(
                                Color.Black,
                                Color(0xFFE53935), // Red
                                Color(0xFF1E88E5), // Blue
                                Color(0xFF43A047), // Green
                                Color(0xFF8E24AA), // Purple
                                Color(0xFFFB8C00)  // Orange
                            )
                            LazyRow(
                                horizontalArrangement = Arrangement.spacedBy(12.dp)
                            ) {
                                items(colors) { color ->
                                    Box(
                                        modifier = Modifier
                                            .size(32.dp)
                                            .clip(CircleShape)
                                            .background(color)
                                            .border(
                                                width = if (currentColor == color) 3.dp else 1.dp,
                                                color = if (currentColor == color) MaterialTheme.colorScheme.primary else Color.LightGray,
                                                shape = CircleShape
                                            )
                                            .clickable { viewModel.setColor(color) }
                                    )
                                }
                            }
                        }

                        // Stroke Width Slider
                        Spacer(modifier = Modifier.height(4.dp))
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            modifier = Modifier.fillMaxWidth(0.9f)
                        ) {
                            Text(
                                text = "Size",
                                style = MaterialTheme.typography.labelSmall
                            )
                            Spacer(modifier = Modifier.width(8.dp))
                            Slider(
                                value = currentStrokeWidth,
                                onValueChange = { viewModel.setStrokeWidth(it) },
                                valueRange = 4f..40f,
                                modifier = Modifier.weight(1f)
                            )
                        }
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Solve Equation Button
                Button(
                    onClick = { viewModel.solveCurrentCanvas() },
                    modifier = Modifier
                        .fillMaxWidth(0.85f)
                        .height(56.dp),
                    shape = RoundedCornerShape(28.dp),
                    colors = ButtonDefaults.buttonColors(
                        containerColor = MaterialTheme.colorScheme.primary
                    ),
                    elevation = ButtonDefaults.buttonElevation(defaultElevation = 6.dp)
                ) {
                    Icon(
                        imageVector = Icons.Default.AutoAwesome,
                        contentDescription = null,
                        modifier = Modifier.padding(end = 8.dp)
                    )
                    Text(
                        text = "Solve Equation (AI)",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.Bold
                    )
                }
            }

            // Loading Overlay
            if (solverUiState is SolverUiState.Loading) {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = Color.Black.copy(alpha = 0.5f)
                ) {
                    Column(
                        horizontalAlignment = Alignment.CenterHorizontally,
                        verticalArrangement = Arrangement.Center
                    ) {
                        CircularProgressIndicator(color = Color.White)
                        Spacer(modifier = Modifier.height(16.dp))
                        Text(
                            text = "Analyzing Equation with AI...",
                            color = Color.White,
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.SemiBold
                        )
                    }
                }
            }

            // Solution Result Sheet
            if (solverUiState is SolverUiState.Success) {
                val solved = (solverUiState as SolverUiState.Success).solvedEquation
                MathResultSheet(
                    solvedEquation = solved,
                    onDismiss = { viewModel.dismissResult() }
                )
            }

            // Settings Dialog
            if (showSettingsDialog) {
                SettingsDialog(
                    currentApiKey = apiKey,
                    useGeminiAi = useGeminiAi,
                    onSaveSettings = { key, useGemini ->
                        viewModel.updateSettings(key, useGemini)
                        Toast.makeText(context, "Settings saved!", Toast.LENGTH_SHORT).show()
                    },
                    onDismiss = { showSettingsDialog = false }
                )
            }

            // History Dialog
            if (showHistoryDialog) {
                AlertDialog(
                    onDismissRequest = { showHistoryDialog = false },
                    title = {
                        Text(
                            text = "Equation History",
                            fontWeight = FontWeight.Bold
                        )
                    },
                    text = {
                        if (history.isEmpty()) {
                            Text("No solved equations yet. Draw an equation and tap Solve!")
                        } else {
                            Column(modifier = Modifier.fillMaxWidth()) {
                                history.forEach { item ->
                                    Card(
                                        modifier = Modifier
                                            .fillMaxWidth()
                                            .padding(vertical = 4.dp)
                                    ) {
                                        Column(modifier = Modifier.padding(12.dp)) {
                                            Text(
                                                text = item.expression,
                                                fontWeight = FontWeight.Bold,
                                                style = MaterialTheme.typography.titleMedium
                                            )
                                            Text(
                                                text = "Answer: ${item.finalAnswer}",
                                                color = MaterialTheme.colorScheme.primary,
                                                fontWeight = FontWeight.SemiBold
                                            )
                                        }
                                    }
                                }
                            }
                        }
                    },
                    confirmButton = {
                        TextButton(onClick = { showHistoryDialog = false }) {
                            Text("Close")
                        }
                    }
                )
            }
        }
    }
}
