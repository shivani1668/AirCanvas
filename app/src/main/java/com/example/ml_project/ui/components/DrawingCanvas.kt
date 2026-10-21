package com.example.ml_project.ui.components

import android.graphics.Bitmap
import android.graphics.Paint
import android.graphics.PorterDuff
import android.graphics.PorterDuffXfermode
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.asAndroidPath
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.nativeCanvas
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.input.pointer.pointerInput
import com.example.ml_project.model.CanvasTool
import com.example.ml_project.model.DrawnPath

@Composable
fun DrawingCanvas(
    paths: List<DrawnPath>,
    currentTool: CanvasTool,
    currentColor: Color,
    currentStrokeWidth: Float,
    isCameraBackground: Boolean,
    onPathAdded: (DrawnPath) -> Unit,
    modifier: Modifier = Modifier
) {
    val currentPath = remember { mutableStateOf<Path?>(null) }
    val currentPoint = remember { mutableStateOf<Offset?>(null) }

    Box(
        modifier = modifier
            .fillMaxSize()
            .background(if (isCameraBackground) Color.Transparent else Color.White)
            .pointerInput(currentTool, currentColor, currentStrokeWidth) {
                detectDragGestures(
                    onDragStart = { offset ->
                        val newPath = Path().apply {
                            moveTo(offset.x, offset.y)
                        }
                        currentPath.value = newPath
                        currentPoint.value = offset
                    },
                    onDrag = { change, dragAmount ->
                        change.consume()
                        currentPoint.value?.let { last ->
                            val next = last + dragAmount
                            currentPath.value?.quadraticTo(
                                last.x,
                                last.y,
                                (last.x + next.x) / 2f,
                                (last.y + next.y) / 2f
                            )
                            currentPoint.value = next
                        }
                    },
                    onDragEnd = {
                        currentPath.value?.let { path ->
                            onPathAdded(
                                DrawnPath(
                                    path = path,
                                    color = if (currentTool == CanvasTool.ERASER) Color.Transparent else currentColor,
                                    strokeWidth = currentStrokeWidth,
                                    isEraser = currentTool == CanvasTool.ERASER
                                )
                            )
                        }
                        currentPath.value = null
                        currentPoint.value = null
                    }
                )
            }
    ) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            // Draw completed paths
            for (drawnPath in paths) {
                if (drawnPath.isEraser) {
                    val nativePaint = Paint().apply {
                        isAntiAlias = true
                        style = Paint.Style.STROKE
                        strokeWidth = drawnPath.strokeWidth
                        strokeCap = Paint.Cap.ROUND
                        strokeJoin = Paint.Join.ROUND
                        xfermode = PorterDuffXfermode(PorterDuff.Mode.CLEAR)
                    }
                    drawContext.canvas.nativeCanvas.drawPath(
                        drawnPath.path.asAndroidPath(),
                        nativePaint
                    )
                } else {
                    drawPath(
                        path = drawnPath.path,
                        color = drawnPath.color,
                        style = Stroke(
                            width = drawnPath.strokeWidth,
                            cap = StrokeCap.Round,
                            join = StrokeJoin.Round
                        )
                    )
                }
            }

            // Draw active in-progress path
            currentPath.value?.let { activePath ->
                if (currentTool == CanvasTool.ERASER) {
                    val nativePaint = Paint().apply {
                        isAntiAlias = true
                        style = Paint.Style.STROKE
                        strokeWidth = currentStrokeWidth
                        strokeCap = Paint.Cap.ROUND
                        strokeJoin = Paint.Join.ROUND
                        xfermode = PorterDuffXfermode(PorterDuff.Mode.CLEAR)
                    }
                    drawContext.canvas.nativeCanvas.drawPath(
                        activePath.asAndroidPath(),
                        nativePaint
                    )
                } else {
                    drawPath(
                        path = activePath,
                        color = currentColor,
                        style = Stroke(
                            width = currentStrokeWidth,
                            cap = StrokeCap.Round,
                            join = StrokeJoin.Round
                        )
                    )
                }
            }
        }
    }
}

/**
 * Converts a list of DrawnPaths into a high-contrast white-background Bitmap for AI image analysis.
 */
fun createBitmapFromPaths(
    paths: List<DrawnPath>,
    width: Int = 1080,
    height: Int = 1080
): Bitmap {
    val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
    val canvas = android.graphics.Canvas(bitmap)
    
    // Draw solid white background
    canvas.drawColor(android.graphics.Color.WHITE)

    val paint = Paint().apply {
        isAntiAlias = true
        style = Paint.Style.STROKE
        strokeCap = Paint.Cap.ROUND
        strokeJoin = Paint.Join.ROUND
    }

    for (drawnPath in paths) {
        if (drawnPath.isEraser) {
            paint.color = android.graphics.Color.WHITE
            paint.strokeWidth = drawnPath.strokeWidth
        } else {
            // High contrast dark stroke on white background
            paint.color = drawnPath.color.toArgb()
            paint.strokeWidth = drawnPath.strokeWidth
        }
        canvas.drawPath(drawnPath.path.asAndroidPath(), paint)
    }

    return bitmap
}
