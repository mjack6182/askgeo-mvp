import { Header } from './components/Header';
import { Chat } from './components/Chat';
import { Footer } from './components/Footer';

function App() {
  return (
    <div className="flex flex-col h-full">
      <Header />
      <main className="flex-1 overflow-hidden">
        <Chat />
      </main>
      <Footer />
    </div>
  );
}

export default App;
