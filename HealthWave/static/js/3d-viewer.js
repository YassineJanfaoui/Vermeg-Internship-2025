// 3D Medical Viewer JavaScript using Three.js

// Global Variables
let scene, camera, renderer, controls;
let currentModel = null;
let isWireframe = false;
let autoRotate = false;
let rotationSpeed = 0;
let originalMaterial = null;

// Color Schemes
const colorSchemes = {
    default: 0x4a90e2,
    medical: 0x0066cc,
    anatomy: 0xff6b6b,
    grayscale: 0x888888
};

// Initialize 3D Viewer
function init3DViewer() {
    const container = document.getElementById('viewer3d');
    if (!container) return;
    
    // Scene setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf0f0f0);
    
    // Camera setup
    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(0, 0, 5);
    
    // Renderer setup
    renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.appendChild(renderer.domElement);
    
    // Controls setup
    if (typeof THREE.OrbitControls !== 'undefined') {
        controls = new THREE.OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.enableZoom = true;
        controls.enablePan = true;
        controls.autoRotate = false;
    }
    
    // Lighting setup
    setupLighting();
    
    // Load default model
    loadNewModel('brain');
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Start animation loop
    animate();
    
    console.log('3D Viewer initialized successfully');
}

// Setup Lighting
function setupLighting() {
    // Ambient light
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    
    // Main directional light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 5, 5);
    directionalLight.castShadow = true;
    directionalLight.shadow.mapSize.width = 2048;
    directionalLight.shadow.mapSize.height = 2048;
    scene.add(directionalLight);
    
    // Fill light
    const fillLight = new THREE.DirectionalLight(0xffffff, 0.3);
    fillLight.position.set(-5, 0, -5);
    scene.add(fillLight);
    
    // Point light for highlights
    const pointLight = new THREE.PointLight(0xffffff, 0.8, 100);
    pointLight.position.set(0, 10, 0);
    scene.add(pointLight);
}

// Load New Model
function loadNewModel(modelType) {
    // Remove existing model
    if (currentModel) {
        scene.remove(currentModel);
    }
    
    // Create new model based on type
    switch(modelType) {
        case 'brain':
            currentModel = createBrainModel();
            break;
        case 'heart':
            currentModel = createHeartModel();
            break;
        case 'lung':
            currentModel = createLungModel();
            break;
        case 'bone':
            currentModel = createBoneModel();
            break;
        default:
            currentModel = createBrainModel();
    }
    
    // Add to scene
    scene.add(currentModel);
    
    // Store original material
    if (currentModel.material) {
        originalMaterial = currentModel.material.clone();
    }
    
    // Reset camera position
    resetView();
}

// Create Brain Model
function createBrainModel() {
    const group = new THREE.Group();
    
    // Main brain geometry
    const brainGeometry = new THREE.SphereGeometry(2, 32, 32);
    
    // Apply some deformation to make it more brain-like
    const vertices = brainGeometry.attributes.position.array;
    for (let i = 0; i < vertices.length; i += 3) {
        const x = vertices[i];
        const y = vertices[i + 1];
        const z = vertices[i + 2];
        
        // Add some organic deformation
        const noise = Math.sin(x * 2) * Math.cos(y * 2) * Math.sin(z * 2) * 0.1;
        vertices[i] += noise;
        vertices[i + 1] += noise * 0.5;
        vertices[i + 2] += noise;
    }
    
    brainGeometry.attributes.position.needsUpdate = true;
    brainGeometry.computeVertexNormals();
    
    const brainMaterial = new THREE.MeshPhongMaterial({
        color: colorSchemes.anatomy,
        shininess: 30,
        transparent: true,
        opacity: 0.9
    });
    
    const brainMesh = new THREE.Mesh(brainGeometry, brainMaterial);
    brainMesh.castShadow = true;
    brainMesh.receiveShadow = true;
    group.add(brainMesh);
    
    // Add brain stem
    const stemGeometry = new THREE.CylinderGeometry(0.3, 0.5, 1.5, 16);
    const stemMaterial = new THREE.MeshPhongMaterial({ color: 0xcc6666 });
    const stemMesh = new THREE.Mesh(stemGeometry, stemMaterial);
    stemMesh.position.y = -1.5;
    group.add(stemMesh);
    
    return group;
}

// Create Heart Model
function createHeartModel() {
    const group = new THREE.Group();
    
    // Heart shape using custom geometry
    const heartShape = new THREE.Shape();
    heartShape.moveTo(0, 0);
    heartShape.bezierCurveTo(0, -0.5, -1, -0.5, -1, 0);
    heartShape.bezierCurveTo(-1, 0.5, -0.5, 1, 0, 0.5);
    heartShape.bezierCurveTo(0.5, 1, 1, 0.5, 1, 0);
    heartShape.bezierCurveTo(1, -0.5, 0, -0.5, 0, 0);
    
    const extrudeSettings = {
        depth: 1,
        bevelEnabled: true,
        bevelSize: 0.1,
        bevelThickness: 0.1
    };
    
    const heartGeometry = new THREE.ExtrudeGeometry(heartShape, extrudeSettings);
    const heartMaterial = new THREE.MeshPhongMaterial({
        color: 0xcc4444,
        shininess: 50
    });
    
    const heartMesh = new THREE.Mesh(heartGeometry, heartMaterial);
    heartMesh.rotation.x = Math.PI;
    heartMesh.scale.set(1.5, 1.5, 1.5);
    heartMesh.castShadow = true;
    group.add(heartMesh);
    
    return group;
}

// Create Lung Model
function createLungModel() {
    const group = new THREE.Group();
    
    // Left lung
    const leftLungGeometry = new THREE.SphereGeometry(1.2, 16, 16);
    leftLungGeometry.scale(0.8, 1.5, 0.6);
    const leftLungMaterial = new THREE.MeshPhongMaterial({
        color: 0x66cc66,
        transparent: true,
        opacity: 0.8
    });
    const leftLung = new THREE.Mesh(leftLungGeometry, leftLungMaterial);
    leftLung.position.x = -1.2;
    leftLung.castShadow = true;
    group.add(leftLung);
    
    // Right lung
    const rightLungGeometry = new THREE.SphereGeometry(1.2, 16, 16);
    rightLungGeometry.scale(0.8, 1.5, 0.6);
    const rightLungMaterial = new THREE.MeshPhongMaterial({
        color: 0x66cc66,
        transparent: true,
        opacity: 0.8
    });
    const rightLung = new THREE.Mesh(rightLungGeometry, rightLungMaterial);
    rightLung.position.x = 1.2;
    rightLung.castShadow = true;
    group.add(rightLung);
    
    // Trachea
    const tracheaGeometry = new THREE.CylinderGeometry(0.2, 0.2, 2, 16);
    const tracheaMaterial = new THREE.MeshPhongMaterial({ color: 0x888888 });
    const trachea = new THREE.Mesh(tracheaGeometry, tracheaMaterial);
    trachea.position.y = 1.5;
    group.add(trachea);
    
    return group;
}

// Create Bone Model
function createBoneModel() {
    const group = new THREE.Group();
    
    // Femur bone simulation
    const boneGeometry = new THREE.CylinderGeometry(0.3, 0.4, 4, 16);
    const boneMaterial = new THREE.MeshPhongMaterial({
        color: 0xf4f4f4,
        shininess: 10
    });
    const boneMesh = new THREE.Mesh(boneGeometry, boneMaterial);
    boneMesh.castShadow = true;
    group.add(boneMesh);
    
    // Bone ends
    const endGeometry = new THREE.SphereGeometry(0.6, 16, 16);
    const endMaterial = new THREE.MeshPhongMaterial({
        color: 0xeeeeee,
        shininess: 10
    });
    
    const topEnd = new THREE.Mesh(endGeometry, endMaterial);
    topEnd.position.y = 2;
    topEnd.scale.set(1, 0.6, 1);
    group.add(topEnd);
    
    const bottomEnd = new THREE.Mesh(endGeometry, endMaterial);
    bottomEnd.position.y = -2;
    bottomEnd.scale.set(1, 0.6, 1);
    group.add(bottomEnd);
    
    return group;
}

// Animation Loop
function animate() {
    requestAnimationFrame(animate);
    
    // Update controls
    if (controls) {
        controls.update();
    }
    
    // Auto-rotation
    if (autoRotate && currentModel) {
        currentModel.rotation.y += rotationSpeed * 0.01;
    }
    
    // Render
    renderer.render(scene, camera);
}

// Window Resize Handler
function onWindowResize() {
    const container = document.getElementById('viewer3d');
    if (!container) return;
    
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
}

// Reset View
function resetView() {
    if (camera && controls) {
        camera.position.set(0, 0, 5);
        controls.reset();
    }
}

// Toggle Wireframe
function toggleWireframe() {
    if (!currentModel) return;
    
    isWireframe = !isWireframe;
    
    currentModel.traverse(function(child) {
        if (child.isMesh) {
            child.material.wireframe = isWireframe;
        }
    });
}

// Set Model Opacity
function setModelOpacity(opacity) {
    if (!currentModel) return;
    
    currentModel.traverse(function(child) {
        if (child.isMesh) {
            child.material.transparent = true;
            child.material.opacity = opacity;
        }
    });
}

// Set Auto Rotation
function setAutoRotation(speed) {
    rotationSpeed = speed;
    autoRotate = speed > 0;
}

// Set Color Scheme
function setColorScheme(scheme) {
    if (!currentModel || !colorSchemes[scheme]) return;
    
    const color = colorSchemes[scheme];
    
    currentModel.traverse(function(child) {
        if (child.isMesh) {
            child.material.color.setHex(color);
        }
    });
}

// Capture Screenshot
function captureScreenshot() {
    if (!renderer) return;
    
    const canvas = renderer.domElement;
    const link = document.createElement('a');
    link.download = 'medical-3d-view.png';
    link.href = canvas.toDataURL();
    link.click();
}

// Export Model (placeholder)
function exportModel() {
    // In a real implementation, this would export the model data
    console.log('Model export functionality would be implemented here');
    alert('Model export feature would download the 3D model file.');
}

// Measurement Tool (placeholder)
function enableMeasurement() {
    console.log('Measurement tool activated');
    // Implementation would allow clicking two points to measure distance
}

// Annotation Tool (placeholder)
function enableAnnotation() {
    console.log('Annotation tool activated');
    // Implementation would allow adding text annotations to the model
}

// Error Handling
function handleError(error) {
    console.error('3D Viewer Error:', error);
    const container = document.getElementById('viewer3d');
    if (container) {
        container.innerHTML = `
            <div class="alert alert-danger h-100 d-flex align-items-center justify-content-center">
                <div class="text-center">
                    <i class="fas fa-exclamation-triangle fa-3x mb-3"></i>
                    <h5>3D Viewer Error</h5>
                    <p>Unable to initialize 3D viewer. Please check your browser compatibility.</p>
                </div>
            </div>
        `;
    }
}

// Check WebGL Support
function checkWebGLSupport() {
    try {
        const canvas = document.createElement('canvas');
        return !!(window.WebGLRenderingContext && (
            canvas.getContext('webgl') || 
            canvas.getContext('experimental-webgl')
        ));
    } catch (e) {
        return false;
    }
}

// Initialize with error handling
try {
    if (!checkWebGLSupport()) {
        throw new Error('WebGL not supported');
    }
    
    // Wait for Three.js to load
    if (typeof THREE === 'undefined') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(init3DViewer, 1000);
        });
    }
} catch (error) {
    handleError(error);
}
