import React, { useState } from 'react';

const InputForm = () => {
  const [formData, setFormData] = useState({
    float1: '',
    float2: '',
    float3: '',
    float4: '',
    float5: '',
    float6: '',
    date: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevData) => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Send data to the Flask backend
    fetch('http://127.0.0.1:5000/api/submit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData)
    })
      .then((response) => response.json())
      .then((data) => {
        console.log('Success:', data);
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  };

  return (
    <form onSubmit={handleSubmit}>
      {[1, 2, 3, 4, 5, 6].map((num) => (
        <div key={num}>
          <label>
            Float {num}:
            <input
              type="number"
              step="any"
              name={`float${num}`}
              value={formData[`float${num}`]}
              onChange={handleChange}
              required
            />
          </label>
        </div>
      ))}
      <div>
        <label>
          Date:
          <input
            type="date"
            name="date"
            value={formData.date}
            onChange={handleChange}
            required
          />
        </label>
      </div>
      <button type="submit">Submit</button>
    </form>
  );
};

export default InputForm;
