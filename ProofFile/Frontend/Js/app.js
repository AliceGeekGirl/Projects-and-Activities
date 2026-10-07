// =========================
// REGISTRO DE CONTRATO
// =========================

const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        const button = document.getElementById("registerButton");
        const result = document.getElementById("registerResult");

        const formData = new FormData(registerForm);

        button.disabled = true;
        button.textContent = "Registrando...";

        result.hidden = true;

        try {

            const response = await fetch(
                "http://127.0.0.1:5000/register",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok) {

                showResult(
                    result,
                    "error",
                    "Não foi possível registrar o contrato.",
                    data.error || "Ocorreu um erro inesperado."
                );

                return;
            }


            showRegisterSuccess(result, data);

            registerForm.reset();

        } catch (error) {

            showResult(
                result,
                "error",
                "Erro ao conectar com o ProofFile.",
                "Verifique se o backend está em execução."
            );

        } finally {

            button.disabled = false;
            button.textContent = "Registrar contrato";

        }

    });

}


// =========================
// VERIFICAÇÃO DE CONTRATO
// =========================

const verifyForm = document.getElementById("verifyForm");

if (verifyForm) {

    verifyForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        const button = document.getElementById("verifyButton");
        const result = document.getElementById("verifyResult");

        const formData = new FormData(verifyForm);

        button.disabled = true;
        button.textContent = "Verificando...";

        result.hidden = true;

        try {

            const response = await fetch(
                "http://127.0.0.1:5000/verify",
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();


            if (!response.ok) {

                showResult(
                    result,
                    "error",
                    "Não foi possível verificar o contrato.",
                    data.error || "Ocorreu um erro inesperado."
                );

                return;
            }


            showVerifyResult(result, data);

        } catch (error) {

            showResult(
                result,
                "error",
                "Erro ao conectar com o ProofFile.",
                "Verifique se o backend está em execução."
            );

        } finally {

            button.disabled = false;
            button.textContent = "Verificar contrato";

        }

    });

}


// =========================
// RESULTADO DO REGISTRO
// =========================

function showRegisterSuccess(result, data) {

    result.className = "result-card success-card";

    result.innerHTML = `
        <div class="result-icon">
            ✓
        </div>

        <h2>
            Registro concluído!
        </h2>

        <p class="result-message">
            O contrato foi registrado com sucesso.
        </p>

        <div class="contract-details">

            <div class="detail">
                <span>Contrato</span>
                <strong>${data.contract_name}</strong>
            </div>

            <div class="detail">
                <span>Código de verificação</span>
                <strong class="verification-code">
                    ${data.verification_code}
                </strong>
            </div>

        </div>

        <div class="blockchain-info">

            <span>
                Registro na Solana
            </span>

            <a
                href="${data.solana_explorer_url}"
                target="_blank"
                rel="noopener noreferrer"
            >
                Ver registro
            </a>

        </div>
    `;

    result.hidden = false;
}


// =========================
// RESULTADO DA VERIFICAÇÃO
// =========================

function showVerifyResult(result, data) {

    if (data.verified) {

        result.className = "result-card success-card";

        result.innerHTML = `
            <div class="result-icon">
                ✓
            </div>

            <h2>
                Contrato verificado
            </h2>

            <p class="result-message">
                O contrato corresponde ao registro.
            </p>

            ${contractDetails(data)}

            ${contractLinks(data)}
        `;

    } else {

        result.className = "result-card error-card";

        result.innerHTML = `
            <div class="result-icon">
                !
            </div>

            <h2>
                Contrato divergente
            </h2>

            <p class="result-message">
                O contrato não corresponde ao registro.
            </p>

            <p class="difference-message">
                O arquivo enviado possui um conteúdo diferente
                do contrato originalmente registrado.
            </p>

            ${contractDetails(data)}

            ${contractLinks(data)}
        `;

    }

    result.hidden = false;
}


// =========================
// INFORMAÇÕES DO CONTRATO
// =========================

function contractDetails(data) {

    return `
        <div class="contract-details">

            <div class="detail">
                <span>Contrato</span>
                <strong>${data.contract_name}</strong>
            </div>

            <div class="detail">
                <span>Empresa</span>
                <strong>${data.company_name}</strong>
            </div>

            <div class="detail">
                <span>Data de registro</span>
                <strong>${data.registration_date}</strong>
            </div>

            <div class="detail">
                <span>Data de término</span>
                <strong>
                    ${data.expiration_date || "Não informada"}
                </strong>
            </div>

            <div class="detail">
                <span>Código de verificação</span>
                <strong class="verification-code">
                    ${data.verification_code}
                </strong>
            </div>

        </div>
    `;
}


// =========================
// LINKS DO RESULTADO
// =========================

function contractLinks(data) {

    return `
        <div class="result-links">

            <a
                href="http://127.0.0.1:5000/contract-file/${data.verification_code}"
                target="_blank"
                class="secondary-button"
            >
                Ver contrato registrado
            </a>

            <a
                href="${data.solana_explorer_url}"
                target="_blank"
                rel="noopener noreferrer"
                class="secondary-button"
            >
                Ver registro na Solana
            </a>

        </div>
    `;
}


// =========================
// RESULTADO GENÉRICO DE ERRO
// =========================

function showResult(
    result,
    type,
    title,
    message
) {

    result.className = `result-card ${type}-card`;

    result.innerHTML = `
        <div class="result-icon">
            !
        </div>

        <h2>
            ${title}
        </h2>

        <p class="result-message">
            ${message}
        </p>
    `;

    result.hidden = false;
}