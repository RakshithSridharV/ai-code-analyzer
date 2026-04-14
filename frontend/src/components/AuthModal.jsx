import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

export default function AuthModal({ onClose }) {
  const { login, register } = useAuth();
  const [tab, setTab]         = useState('login');   // 'login' | 'register'
  const [email, setEmail]     = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPass, setShowPass] = useState(false);
  const [error, setError]     = useState('');
  const [loading, setLoading] = useState(false);

  const reset = (newTab) => {
    setTab(newTab);
    setError('');
    setEmail('');
    setUsername('');
    setPassword('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      if (tab === 'login') {
        await login(email, password);
      } else {
        await register(email, username, password);
      }
      onClose();
    } catch (err) {
      setError(err.message || 'Something went wrong');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={e => e.stopPropagation()}>

        {/* Header */}
        <div className="auth-modal-header">
          <div className="auth-logo">✦ ASTra</div>
          <button className="auth-close-btn" onClick={onClose} title="Close">✕</button>
        </div>

        {/* Tab switcher */}
        <div className="auth-tabs">
          <button
            id="auth-tab-login"
            className={`auth-tab ${tab === 'login' ? 'auth-tab-active' : ''}`}
            onClick={() => reset('login')}
          >
            Sign In
          </button>
          <button
            id="auth-tab-register"
            className={`auth-tab ${tab === 'register' ? 'auth-tab-active' : ''}`}
            onClick={() => reset('register')}
          >
            Create Account
          </button>
          <div className={`auth-tab-indicator ${tab === 'register' ? 'auth-tab-indicator-right' : ''}`} />
        </div>

        {/* Form */}
        <form className="auth-form" onSubmit={handleSubmit} noValidate>
          <div className="auth-field">
            <label className="auth-label" htmlFor="auth-email">Email</label>
            <input
              id="auth-email"
              className="auth-input"
              type="email"
              placeholder="you@example.com"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </div>

          {tab === 'register' && (
            <div className="auth-field">
              <label className="auth-label" htmlFor="auth-username">Username</label>
              <input
                id="auth-username"
                className="auth-input"
                type="text"
                placeholder="devguru42"
                value={username}
                onChange={e => setUsername(e.target.value)}
                required
                minLength={3}
                maxLength={32}
                autoComplete="username"
              />
            </div>
          )}

          <div className="auth-field">
            <label className="auth-label" htmlFor="auth-password">Password</label>
            <div className="auth-pass-wrap">
              <input
                id="auth-password"
                className="auth-input"
                type={showPass ? 'text' : 'password'}
                placeholder={tab === 'register' ? 'At least 6 characters' : '••••••••'}
                value={password}
                onChange={e => setPassword(e.target.value)}
                required
                autoComplete={tab === 'login' ? 'current-password' : 'new-password'}
              />
              <button
                type="button"
                className="auth-pass-toggle"
                onClick={() => setShowPass(v => !v)}
                tabIndex={-1}
                title={showPass ? 'Hide password' : 'Show password'}
              >
                {showPass ? '🙈' : '👁'}
              </button>
            </div>
          </div>

          {error && <div className="auth-error" role="alert">{error}</div>}

          <button
            id="auth-submit-btn"
            className="auth-submit"
            type="submit"
            disabled={loading}
          >
            {loading ? (
              <><span className="auth-spinner" /> {tab === 'login' ? 'Signing in…' : 'Creating account…'}</>
            ) : (
              tab === 'login' ? '🔐 Sign In' : '🚀 Create Account'
            )}
          </button>
        </form>

        {/* Footer toggle */}
        <p className="auth-footer">
          {tab === 'login' ? (
            <>Don't have an account?{' '}
              <button className="auth-link" onClick={() => reset('register')}>Sign up</button>
            </>
          ) : (
            <>Already have an account?{' '}
              <button className="auth-link" onClick={() => reset('login')}>Sign in</button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
