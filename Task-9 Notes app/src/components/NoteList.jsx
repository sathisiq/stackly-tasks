import React from 'react'
import NoteCard from './NoteCard'

export default function NoteList({ notes, onDelete }) {
  if (!notes || notes.length === 0) {
    return <div className="empty">No notes yet. Add your first note above.</div>
  }

  return (
    <div className="notes">
      {notes.map(note => (
        <NoteCard key={note.id} note={note} onDelete={onDelete} />
      ))}
    </div>
  )
}
