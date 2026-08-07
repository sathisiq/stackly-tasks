import React, { useEffect, useState } from 'react'
import NoteForm from './components/NoteForm'
import SearchBar from './components/SearchBar'
import NoteList from './components/NoteList'

export default function App() {
  const [notes, setNotes] = useState([])
  const [search, setSearch] = useState('')
  const [category, setCategory] = useState('All')

  useEffect(() => {
    const raw = localStorage.getItem('notes')
    if (raw) setNotes(JSON.parse(raw))
  }, [])

  useEffect(() => {
    localStorage.setItem('notes', JSON.stringify(notes))
  }, [notes])

  function addNote(note) {
    setNotes(prev => [{ ...note, id: Date.now() }, ...prev])
  }

  function deleteNote(id) {
    setNotes(prev => prev.filter(n => n.id !== id))
  }

  const filtered = notes.filter(n => {
    const matchesSearch = n.title.toLowerCase().includes(search.toLowerCase())
    const matchesCategory = category === 'All' ? true : n.category === category
    return matchesSearch && matchesCategory
  })

  return (
    <div className="container">
      <h1>Personal Notes</h1>
      <NoteForm onAdd={addNote} />
      <SearchBar
        search={search}
        category={category}
        onSearchChange={setSearch}
        onCategoryChange={setCategory}
      />

      <div className="meta">You have {notes.length} notes</div>

      <NoteList notes={filtered} onDelete={deleteNote} />
    </div>
  )
}
