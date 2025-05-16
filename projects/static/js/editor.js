document.addEventListener('DOMContentLoaded', function() {
    // Inicializar o editor CodeMirror
    const codeEditor = CodeMirror.fromTextArea(document.getElementById('code-editor'), {
        mode: 'python',
        theme: 'monokai',
        lineNumbers: true,
        indentUnit: 4,
        indentWithTabs: false,
        smartIndent: true,
        tabSize: 4,
        autoCloseBrackets: true,
        matchBrackets: true,
        extraKeys: {
            "Tab": function(cm) {
                cm.replaceSelection("    ", "end");
            }
        }
    });

    // Botão para executar o código
    const runButton = document.getElementById('run-code');
    const outputDiv = document.getElementById('output');
    const outputTab = document.getElementById('output-tab');

    runButton.addEventListener('click', function() {
        // Obter o código do editor
        const code = codeEditor.getValue();
        
        // Mostrar indicador de carregamento
        outputDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Executando...</span></div><p>Executando o código...</p></div>';
        
        // Mudar para a aba de saída
        outputTab.click();
        
        // Enviar o código para o servidor para execução
        fetch('/api/execute-code', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json; charset=utf-8'
            },
            body: JSON.stringify({ code: code })
        })
        .then(response => response.json())
        .then(data => {
            // Exibir a saída
            if (data.returncode === 0) {
                // Execução bem-sucedida
                outputDiv.innerHTML = '<pre class="success">' + (data.stdout || 'Programa executado com sucesso (sem saída).') + '</pre>';
            } else {
                // Erro na execução
                outputDiv.innerHTML = '<pre class="error">' + (data.stderr || 'Erro desconhecido.') + '</pre>';
            }
        })
        .catch(error => {
            outputDiv.innerHTML = '<pre class="error">Erro ao executar o código: ' + error.message + '</pre>';
        });
    });

    // Botão para verificar o exercício (se estiver em um exercício)
    const checkButton = document.getElementById('check-exercise');
    if (checkButton && exerciseId) {
        checkButton.addEventListener('click', function() {
            // Obter o código do editor
            const code = codeEditor.getValue();
            
            // Mostrar indicador de carregamento
            outputDiv.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Verificando...</span></div><p>Verificando a solução...</p></div>';
            
            // Mudar para a aba de saída
            outputTab.click();
            
            // Enviar o código para o servidor para verificação
            fetch('/api/check-exercise', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json; charset=utf-8'
                },
                body: JSON.stringify({ 
                    exercise_id: exerciseId,
                    code: code 
                })
            })
            .then(response => response.json())
            .then(data => {
                // Exibir o resultado da verificação
                if (data.success) {
                    outputDiv.innerHTML = '<div class="alert alert-success">' + 
                        '<h4 class="alert-heading">Parabéns!</h4>' +
                        '<p>' + data.message + '</p>' +
                        (data.output ? '<pre>' + data.output + '</pre>' : '') +
                        '</div>';
                } else {
                    outputDiv.innerHTML = '<div class="alert alert-danger">' +
                        '<h4 class="alert-heading">Não passou nos testes</h4>' +
                        '<p>' + data.message + '</p>' +
                        (data.output ? '<pre>' + data.output + '</pre>' : '') +
                        '</div>';
                }
            })
            .catch(error => {
                outputDiv.innerHTML = '<pre class="error">Erro ao verificar o exercício: ' + error.message + '</pre>';
            });
        });
    }

    // Função para redimensionar o editor quando a janela é redimensionada
    function resizeEditor() {
        const editorElement = document.querySelector('.CodeMirror');
        if (editorElement) {
            const windowHeight = window.innerHeight;
            const editorTop = editorElement.getBoundingClientRect().top;
            const footerHeight = 100; // Altura aproximada do footer
            const newHeight = windowHeight - editorTop - footerHeight;
            
            if (newHeight >= 300) { // Altura mínima
                editorElement.style.height = newHeight + 'px';
            }
        }
    }

    // Redimensionar o editor quando a página carrega e quando a janela é redimensionada
    window.addEventListener('resize', resizeEditor);
    setTimeout(resizeEditor, 100); // Pequeno atraso para garantir que o editor foi renderizado
});