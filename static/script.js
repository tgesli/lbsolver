document.addEventListener('DOMContentLoaded', function() {
    const solveBtn = document.getElementById('solveBtn');
    const resultsDiv = document.getElementById('results');
    const solutionsList = document.getElementById('solutionsList');
    const letterInputs = document.querySelectorAll('.letter-input');

    console.log('DOM loaded, found elements:', {
        solveBtn: !!solveBtn,
        resultsDiv: !!resultsDiv,
        solutionsList: !!solutionsList,
        letterInputs: letterInputs.length
    });

    // Handle input validation and auto-focus
    letterInputs.forEach((input, index) => {
        input.addEventListener('input', function() {
            if (this.value.length === 1) {
                // Move to next input, or first input if at the end
                const nextIndex = (index + 1) % letterInputs.length;
                letterInputs[nextIndex].focus();
            }
        });

        // Allow only letters
        input.addEventListener('keypress', function(e) {
            if (!/[a-zA-Z]/.test(e.key)) {
                e.preventDefault();
            }
        });
    });

    solveBtn.addEventListener('click', async function() {
        console.log('Solve button clicked');
        
        // Get puzzle state
        const letters = Array.from(letterInputs).map(input => input.value.toUpperCase());
        console.log('Raw letters from inputs:', letters);
        
        // Check if all inputs are filled
        if (letters.some(letter => !letter)) {
            console.log('Missing letters detected');
            alert('Please fill in all letters');
            return;
        }

        // Show loading state
        solveBtn.disabled = true;
        solveBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Solving...';
        resultsDiv.classList.add('d-none');
        solutionsList.innerHTML = '';

        try {
            // Convert letters array to the format expected by the solver
            const puzzle = [
                letters.slice(0, 3).join(''),  // top
                letters.slice(3, 6).join(''),  // right
                letters.slice(6, 9).join(''),  // bottom
                letters.slice(9, 12).join('')  // left
            ];

            console.log('Formatted puzzle data:', puzzle);

            const response = await fetch('/solve', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ puzzle }),
            });

            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Response data:', data);

            if (data.success) {
                console.log('Success! Number of solutions:', data.solutions.length);
                // Display solutions
                data.solutions.forEach((solution, index) => {
                    console.log(`Solution ${index + 1}:`, solution);
                    const solutionDiv = document.createElement('div');
                    solutionDiv.className = 'list-group-item solution-item';
                    solutionDiv.innerHTML = `
                        <div class="solution-words">${solution.words.join(' → ')}</div>
                        <div class="solution-score">Score: ${solution.score}</div>
                    `;
                    solutionsList.appendChild(solutionDiv);
                });

                resultsDiv.classList.remove('d-none');
            } else {
                console.error('Error from server:', data.error);
                alert('Error: ' + data.error);
            }
        } catch (error) {
            console.error('Error during solve:', error);
            alert('Error solving puzzle: ' + error.message);
        } finally {
            // Reset button state
            solveBtn.disabled = false;
            solveBtn.textContent = 'Solve Puzzle';
        }
    });
}); 