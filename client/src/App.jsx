import "./App.css";
import VapiWidget from "./components/VapiWidget";

function App() {
  return (
    <>
      {/* VapiWidget usage */}
      <VapiWidget
        apiKey={import.meta.env.VITE_VAPI_API_KEY}
        assistantId={import.meta.env.VITE_VAPI_ASSISTANT_ID}
      />
    </>
  );
}

export default App;
