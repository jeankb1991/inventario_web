const API_BASE = '';

let table;
function formatCurrency(v){ return v? Number(v).toFixed(2) : '0.00'; }

function loadItems(){
  fetch(API_BASE + '/api/items').then(r=>r.json()).then(data=>{
    if (table) { table.clear().rows.add(data).draw(); return; }
    table = $('#itemsTable').DataTable({
      data: data,
      columns: [
        { data: 'id' },
        { data: 'nome' },
        { data: 'local' },
        { data: 'modelo' },
        { data: 'valor', render: d => formatCurrency(d) },
        { data: null, orderable:false, render: function(row){
            return `<a class="btn btn-sm btn-primary me-1" href="/uploads/${row.imagem ? row.imagem.split('/').pop() : ''}" target="_blank">Ver</a>
                    <button class="btn btn-sm btn-warning me-1" onclick="editItem(${row.id})">Editar</button>
                    <button class="btn btn-sm btn-danger" onclick="deleteItem(${row.id})">Apagar</button>`;
        }}
      ]
    });
  }).catch(e=>console.error(e));
}

function resetForm(){
  document.getElementById('itemForm').reset();
  document.getElementById('preview').style.display = 'none';
  document.getElementById('preview').src = '#';
  document.getElementById('itemId').value = '';
}

document.addEventListener('DOMContentLoaded', function(){
  loadItems();

  document.getElementById('imagem').addEventListener('change', function(e){
    const file = this.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = function(ev){ 
      const p = document.getElementById('preview');
      p.src = ev.target.result;
      p.style.display = 'block';
    }
    reader.readAsDataURL(file);
  });

  document.getElementById('itemForm').addEventListener('submit', function(ev){
    ev.preventDefault();
    const id = document.getElementById('itemId').value;
    const form = new FormData(this);
    const method = id ? 'PUT' : 'POST';
    const url = id ? (`/api/items/${id}`) : ('/api/items');
    fetch(url, { method: method, body: form })
      .then(r=>{
        if (!r.ok) return r.text().then(t=>{ throw new Error(t) });
        return r.json();
      })
      .then(()=>{ 
        const modalEl = document.getElementById('itemModal');
        const modal = bootstrap.Modal.getInstance(modalEl) || new bootstrap.Modal(modalEl);
        modal.hide();
        resetForm(); 
        loadItems(); 
      })
      .catch(err=>{ console.error(err); alert('Erro ao salvar. Veja console.'); });
  });

  document.getElementById('btnAdd').addEventListener('click', resetForm);

  document.getElementById('btnPDF').addEventListener('click', () => {
    window.open('/api/pdf', '_blank');
  });
});

function editItem(id){
  fetch('/api/items').then(r=>r.json()).then(data=>{
    const item = data.find(x=>x.id===id);
    if (!item) return alert('Item não encontrado.');
    document.getElementById('itemId').value = item.id;
    document.getElementById('nome').value = item.nome;
    document.getElementById('local').value = item.local;
    document.getElementById('modelo').value = item.modelo;
    document.getElementById('data_compra').value = item.data_compra || '';
    document.getElementById('valor').value = item.valor || '';
    document.getElementById('serie').value = item.serie;
    document.getElementById('descricao').value = item.descricao;
    if (item.imagem){
      const p = document.getElementById('preview');
      p.src = '/uploads/' + item.imagem.split('/').pop();
      p.style.display = 'block';
    }
    const modalEl = document.getElementById('itemModal');
    const modal = new bootstrap.Modal(modalEl);
    modal.show();
  });
}

function deleteItem(id){
  if (!confirm('Confirma exclusão?')) return;
  fetch(`/api/items/${id}`, { method: 'DELETE' })
    .then(r=>r.json()).then(()=> loadItems())
    .catch(e=>{ console.error(e); alert('Erro ao deletar.'); });
}
