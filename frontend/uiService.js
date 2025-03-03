export class UIService {
    static updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.innerHTML = content;
        }
    }

    static addListItem(listId, content) {
        const list = document.getElementById(listId);
        if (list) {
            const listItem = document.createElement('li');
            listItem.textContent = content;
            list.appendChild(listItem);
        }
    }
}
