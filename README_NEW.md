# travel-booking-app

Este projeto é uma aplicação web de reservas de viagens, desenvolvida para fornecer uma interface intuitiva para usuários buscarem e reservarem serviços de viagem. A arquitetura é modular, separando a interface do usuário (frontend) dos serviços de API (backend), visando escalabilidade e manutenção.

## Funcionalidades

*   **Interface de Reserva Interativa:** Proporciona uma experiência de usuário moderna e responsiva para a busca e seleção de opções de viagem, utilizando componentes UI acessíveis e reusáveis.
*   **Gerenciamento de Formulários Robustos:** Implementa formulários complexos com validação e gestão de estado eficientes, garantindo a integridade dos dados inseridos pelos usuários.
*   **Navegação e Estrutura de Conteúdo:** Oferece menus de navegação, diálogos e estruturas de layout bem definidas para organizar as informações de viagem de forma clara.
*   **Arquitetura Frontend-Backend:** Separação clara entre a aplicação cliente (desenvolvida com Vite/React) e os serviços de backend (Node.js), permitindo desenvolvimento e deploy independentes.

## Stack de Tecnologias

O projeto utiliza uma combinação de tecnologias modernas para uma experiência de desenvolvimento e de usuário otimizada:

*   **Linguagem Principal:** JavaScript (Node.js)
*   **Framework Frontend:** React (presumido via `vite.config.ts`, `src/` e dependências UI)
*   **Build Tool:** [Vite](https://vitejs.dev/)
*   **Estilização:** [Tailwind CSS](https://tailwindcss.com/)
*   **Componentes UI:** [Radix UI](https://www.radix-ui.com/) (ex: `@radix-ui/react-accordion`, `@radix-ui/react-alert-dialog`, `@radix-ui/react-dialog`, `@radix-ui/react-dropdown-menu`, `@radix-ui/react-select`, entre outros)
*   **Gerenciamento de Formulários:** `@hookform/resolvers` (provavelmente integrado com [React Hook Form](https://react-hook-form.com/))
*   **Linter:** [ESLint](https://eslint.org/)

## Instalação

Para configurar e rodar o projeto localmente, siga os passos abaixo:

1.  Clone o repositório:
    ```bash
    git clone https://github.com/mauricegss/travel-booking-app.git
    ```
2.  Navegue até o diretório do projeto:
    ```bash
    cd travel-booking-app
    ```
3.  Instale as dependências principais do projeto:
    ```bash
    npm install
    # ou
    # yarn install
    ```

## Como Usar

Após a instalação das dependências, você pode iniciar o servidor de desenvolvimento do frontend:

1.  Inicie a aplicação em modo de desenvolvimento:
    ```bash
    npm run dev
    ```
2.  A aplicação estará disponível em `http://localhost:5173` (ou porta similar indicada pelo Vite).

**Observação:** Este projeto inclui um diretório `backend/` para os serviços de API. As instruções específicas de instalação e execução para o backend não foram fornecidas no escopo das dependências principais e exigem consulta à documentação interna do diretório `backend/`, caso exista um `package.json` separado ou um `README.md` específico.