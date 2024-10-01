import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.169.0/+esm';
import * as CANNON from 'https://cdn.jsdelivr.net/npm/cannon-es@0.20.0/dist/cannon-es.min.js';
import CameraControls from 'https://cdn.jsdelivr.net/npm/camera-controls@2.9.0/+esm';
import { DiceManager, DiceD4, DiceD6, DiceD8, DiceD10, DiceD12, DiceD20 } from './dice.js';

CameraControls.install( { THREE: THREE } );

var scene = new THREE.Scene();
var camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0,30,30);

scene.add(camera);
var renderer = new THREE.WebGLRenderer({antialias:true} );
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const cameraControls = new CameraControls( camera, renderer.domElement );

var world = new CANNON.World();
DiceManager.setWorld(world);

let diceArray = [];

function createDice(type, value) {
    let dice;
    switch(type) {
        case 'd4': dice = new DiceD4(); break;
        case 'd6': dice = new DiceD6(); break;
        case 'd8': dice = new DiceD8(); break;
        case 'd10': dice = new DiceD10(); break;
        case 'd12': dice = new DiceD12(); break;
        default: break;
    }

    if (dice) {
        // If you want to place the mesh somewhere else, you have to update the body
        dice.getObject().position.x = 150;
        dice.getObject().position.y = 100;
        dice.getObject().rotation.x = 20 * Math.PI / 180;
        dice.updateBodyFromMesh();

        scene.add(dice.getObject());
        diceArray.push({ dice: dice, value: value });
    }
}
console.log(diceOptions);
diceOptions.forEach(option => {
    const [type, values] = option;
    values.forEach(value => {
        createDice(type, value);
    });
});

DiceManager.prepareValues(diceArray);

function animate() {
    world.step(1.0 / 60.0);
    console.log(diceArray);
    diceArray.forEach(diceObj => {
        diceObj.dice.updateMeshFromBody();
    });

    renderer.render(scene, camera);
    requestAnimationFrame(animate);
}

requestAnimationFrame(animate);
