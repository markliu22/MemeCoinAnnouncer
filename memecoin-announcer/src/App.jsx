import { useState } from 'react';
import './App.css';

function App() {
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');

  const handleSubscribe = async () => {
    try {
      const response = await fetch('http://localhost:5001/subscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, phone }),
      });
      
      const data = await response.json();
      
      if (response.ok) {
        alert('Successfully subscribed!');
        setEmail('');
        setPhone('');
      } else {
        alert(`Subscription failed: ${data.error || 'Please try again.'}`);
      }
    } catch (error) {
      console.error('Error details:', error);
      alert('Error subscribing. Please try again later.');
    }
  };

  const handleUnsubscribe = async () => {
    try {
      const response = await fetch('http://localhost:5001/unsubscribe', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, phone }),
      });
      
      if (response.ok) {
        alert('Successfully unsubscribed!');
        setEmail('');
        setPhone('');
      } else {
        alert('Unsubscription failed. Please try again.');
      }
    } catch (error) {
      alert('Error unsubscribing. Please try again later.');
    }
  };

  return (
    <div className="container">
      <h1>Welcome to MemeCoinAnnouncer 🚀</h1>
      <p>Get notified when crypto influencers mention new tokens!</p>
      
      <div className="form">
        <input
          type="email"
          placeholder="Enter your email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          type="tel"
          placeholder="Enter your phone number"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
        />
        <div className="buttons">
          <button onClick={handleSubscribe}>Subscribe</button>
          <button onClick={handleUnsubscribe} className="unsubscribe">
            Unsubscribe
          </button>
        </div>
      </div>
    </div>
  );
}

export default App;