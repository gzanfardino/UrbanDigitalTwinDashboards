window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, layer, context) {
            const id = feature.properties.id_edifici;
            const risk = feature.properties.risk_level;

            const popupContent = `
        <div>
            <h4 style="margin:0;">Building ID: ${id}</h4>
            <p style="margin:0;">Risk Level: ${risk}</p>
            <br>
            <select id="dropdown-${id}">
                <option value="Low" ${risk === "Low" ? "selected" : ""}>Low Risk</option>
                <option value="Medium" ${risk === "Medium" ? "selected" : ""}>Medium Risk</option>
                <option value="High" ${risk === "High" ? "selected" : ""}>High Risk</option>
            </select>
        </div>
    `;

            layer.bindPopup(popupContent, {
                sticky: true,
                direction: "top",
                className: "custom-tooltip"
            });
        }

    }
});