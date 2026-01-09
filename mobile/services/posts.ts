/**
 * Posts service - To be implemented by students
 *
 * This file contains stub functions for posts, quizzes, and file functionality.
 * Students will implement these endpoints as part of their coursework.
 */

// Posts functionality will be implemented by students
export async function getPost(_postId: number) {
    throw new Error(
        'Posts functionality not yet implemented. Students will implement this.'
    );
}

export async function getPostFile(_postId: number) {
    throw new Error(
        'File posts functionality not yet implemented. Students will implement this.'
    );
}

// Quiz functionality will be implemented by students
export async function getQuiz(_quizId: number) {
    throw new Error(
        'Quiz functionality not yet implemented. Students will implement this.'
    );
}

export async function startQuizAttempt(_quizId: number) {
    throw new Error(
        'Quiz attempts functionality not yet implemented. Students will implement this.'
    );
}

export async function submitQuizAttempt(
    _attemptId: number,
    _responses: unknown
) {
    throw new Error(
        'Quiz submission functionality not yet implemented. Students will implement this.'
    );
}
