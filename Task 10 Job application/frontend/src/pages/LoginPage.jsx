import { useContext } from 'react'
import { AuthContext } from '../App'
import AuthForm from './AuthForm'
export default function LoginPage() { const { setUser } = useContext(AuthContext); return <AuthForm onLogin={setUser} /> }
