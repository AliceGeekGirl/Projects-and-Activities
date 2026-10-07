const BACKEND_URL = "http://127.0.0.1:5000";


/*
 * Cria o link para a transação da Solana.
 *
 * O Backend retorna apenas a assinatura da transação.
 * Aqui transformamos essa assinatura em um link
 * para o Solana Explorer da Devnet.
 */
function createSolanaExplorerUrl(transaction) {

    if (!transaction) {
        return null;
    }

    return `https://explorer.solana.com/tx/${transaction}?cluster=devnet`;
}


/*
 * Formata uma data recebida pelo Backend.
 *
 * Exemplo:
 * 2026-10-07 → 07/10/2026
 */
function formatDate(date) {

    if (!date) {
        return "Não informada";
    }

    const parts = date.split("-");

    if (parts.length !== 3) {
        return date;
    }

    return `${parts[2]}/${parts[1]}/${parts[0]}`;
}


/*
 * Cria o HTML com as informações do contrato.
 */
function contractDetails(data) {

    return `
        <div class="result-details">

            <div class="detail-item">
                <span>Contrato</span>
                <strong>${data.contract_name}</strong>
            </div>

            ${
                data.company_name
                    ? `
                    <div class="detail-item">
                        <span>Empresa</span>
                        <strong>${data.company_name}</strong>
                    </div>
                    `
                    : ""
            }

            <div class="detail-item">
                <span>Código de verificação</span>
                <strong>${data.verification_code}</strong>
            </div>

            <div class="detail-item">
                <span>Data de registro</span>
                <strong>${formatDate(data.registration_date)}</strong>
            </div>

            ${
                data.expiration_date
                    ? `
                    <div class="detail-item">
                        <span>Data de término</span>
                        <strong>${formatDate(data.expiration_date)}</strong>
                    </div>
                    `
                    : ""
            }

        </div>
    `;
}


/*
 * Cria o link para o contrato registrado.
 */
function contractFileLink(verificationCode) {

    if (!verificationCode) {
        return "";
    }

    const url =
        `${BACKEND_URL}/contract-file/${verificationCode}`;

    return `
        <a
            href="${url}"
            target="_blank"
            rel="noopener noreferrer"
            class="secondary-button"
        >
            Ver contrato registrado
        </a>
    `;
}


/*
 * Cria o link para a transação na Solana.
 */
function solanaLink(transaction) {

    const url = createSolanaExplorerUrl(transaction);

    if (!url) {
        return "";
    }

    return `
        <a
            href="${url}"
            target="_blank"
            rel="noopener noreferrer"
            class="blockchain-link"
        >
            Ver registro na Solana
        </a>
    `;
}


/*
 * Mostra o resultado do REGISTRO.
 */
function showRegisterSuccess(data) {

    const result = document.getElementById("registerResult");
    const formCard = document.getElementById("registerCard");

    result.hidden = false;

    result.innerHTML = `
        <div class="result-icon">
            ✓
        </div>

        <h2>
            ${data.message}
        </h2>

        <p class="result-description">
            Seu contrato foi registrado com sucesso.
            Guarde o código de verificação para futuras consultas.
        </p>

        <div class="verification-code-box">

            <span>
                Código de verificação
            </span>

            <strong>
                ${data.verification_code}
            </strong>

        </div>

        ${contractDetails(data)}

        <div class="result-actions">

            ${contractFileLink(data.verification_code)}

            ${solanaLink(data.solana_transaction)}

        </div>
    `;

    formCard.hidden = true;

    result.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


/*
 * Mostra o resultado da VERIFICAÇÃO.
 */
function showVerifyResult(data) {

    const result = document.getElementById("verifyResult");
    const formCard = document.getElementById("verifyCard");

    result.hidden = false;

    const isVerified = data.verified;

    result.className =
        `result-card ${
            isVerified
                ? "verified-result"
                : "invalid-result"
        }`;

    result.innerHTML = `
        <div class="result-icon">
            ${isVerified ? "✓" : "!"}
        </div>

        <h2>
            ${data.message}
        </h2>

        <p class="result-description">
            ${
                isVerified
                    ? "O arquivo enviado corresponde ao contrato originalmente registrado."
                    : "O arquivo enviado possui um conteúdo diferente do contrato originalmente registrado."
            }
        </p>

        ${contractDetails(data)}

        <div class="result-actions">

            ${contractFileLink(data.verification_code)}

            ${solanaLink(data.solana_transaction)}

        </div>
    `;

    formCard.hidden = true;

    result.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


/*
 * Mostra uma mensagem de erro.
 */
function showError(result, message) {

    result.hidden = false;

    result.className = "result-card error-result";

    result.innerHTML = `
        <div class="result-icon">
            !
        </div>

        <h2>
            Não foi possível concluir a operação.
        </h2>

        <p class="result-description">
            ${message}
        </p>
    `;

    result.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


/*
 * REGISTRO DE CONTRATO
 */
const registerForm = document.getElementById("registerForm");

if (registerForm) {

    registerForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        const button =
            document.getElementById("registerButton");

        const result =
            document.getElementById("registerResult");

        const formData = new FormData(registerForm);

        button.disabled = true;
        button.textContent = "Registrando contrato...";

        result.hidden = true;

        try {

            const response = await fetch(
                `${BACKEND_URL}/register`,
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok) {

                showError(
                    result,
                    data.error || "Ocorreu um erro ao registrar o contrato."
                );

                button.disabled = false;
                button.textContent = "Registrar contrato";

                return;
            }

            showRegisterSuccess(data);

        } catch (error) {

            showError(
                result,
                "Não foi possível conectar ao Backend."
            );

            button.disabled = false;
            button.textContent = "Registrar contrato";
        }

    });
}


/*
 * VERIFICAÇÃO DE CONTRATO
 */
const verifyForm = document.getElementById("verifyForm");

if (verifyForm) {

    verifyForm.addEventListener("submit", async (event) => {

        event.preventDefault();

        const button =
            document.getElementById("verifyButton");

        const result =
            document.getElementById("verifyResult");

        const formData = new FormData(verifyForm);

        button.disabled = true;
        button.textContent = "Verificando contrato...";

        result.hidden = true;

        try {

            const response = await fetch(
                `${BACKEND_URL}/verify`,
                {
                    method: "POST",
                    body: formData
                }
            );

            const data = await response.json();

            if (!response.ok) {

                showError(
                    result,
                    data.error || "Ocorreu um erro ao verificar o contrato."
                );

                button.disabled = false;
                button.textContent = "Verificar contrato";

                return;
            }

            showVerifyResult(data);

        } catch (error) {

            showError(
                result,
                "Não foi possível conectar ao Backend."
            );

            button.disabled = false;
            button.textContent = "Verificar contrato";
        }

    });
}