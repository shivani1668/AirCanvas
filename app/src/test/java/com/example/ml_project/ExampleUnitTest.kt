package com.example.ml_project

import com.example.ml_project.engine.FreeMathSolverEngine
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ExampleUnitTest {

    @Test
    fun testArithmeticSolver() {
        val result = FreeMathSolverEngine.solveExpression("2 + 3 * 4")
        assertEquals("14", result.finalAnswer)
        assertEquals("Arithmetic", result.category)
        assertTrue(result.solutionSteps.isNotEmpty())
    }

    @Test
    fun testLinearEquationSolver() {
        val result = FreeMathSolverEngine.solveExpression("2x + 10 = 30")
        assertEquals("x = 10", result.finalAnswer)
        assertEquals("Algebra (Linear Equation)", result.category)
        assertTrue(result.solutionSteps.size >= 3)
    }

    @Test
    fun testCalculusDerivative() {
        val result = FreeMathSolverEngine.solveExpression("d/dx(x^2)")
        assertEquals("2x", result.finalAnswer)
        assertEquals("Calculus (Differentiation)", result.category)
    }
}
