import React, { useState } from 'react'

export default function NoteForm({ onAdd }) {
  const [title, setTitle] = useState('')
  const [content, setContent] = useState('')
  const [category, setCategory] = useState('Work')

  function submit(e) {
    e.preventDefault()
    if (!title.trim()) return
    onAdd({ title, content, category })
    setTitle('')
    setContent('')
    setCategory('Work')
  }

  return (
    <form className="form" onSubmit={submit}>
      <div className="form-row">
        <input
          placeholder="Title"
          value={title}
          onChange={e => setTitle(e.target.value)}
        />

        <select value={category} onChange={e => setCategory(e.target.value)}>
          <option>Work</option>
          <option>Personal</option>
          <option>Study</option>
          <option>Other</option>
        </select>

        <button className="btn" type="submit">Add</button>
      </div>

      <textarea
        placeholder="Content (optional)"
        value={content}
        onChange={e => setContent(e.target.value)}
      />
    </form>
  )
}
